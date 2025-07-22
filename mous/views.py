from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse, Http404
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_sameorigin
import json
from datetime import datetime, timedelta

from .models import MOU, ActivityLog, ShareLink, PartnerSubmission
from .forms import MOUForm, PartnerSubmissionForm
from .utils import get_client_ip, extract_pdf_data, log_activity


class MOUListView(LoginRequiredMixin, ListView):
    model = MOU
    template_name = 'mous/mou_list.html'
    context_object_name = 'mous'
    paginate_by = 12

    def get_queryset(self):
        queryset = MOU.objects.all()
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(partner_name__icontains=search) |
                Q(partner_organization__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Sort functionality
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['title', '-title', 'expiry_date', '-expiry_date', 'partner_name', '-partner_name', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort_by)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = MOU.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        context['current_search'] = self.request.GET.get('search', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        
        # Statistics
        context['total_mous'] = MOU.objects.count()
        context['active_mous'] = MOU.objects.filter(status='approved').count()
        context['expiring_soon'] = MOU.objects.filter(
            status='approved',
            expiry_date__lte=datetime.now().date() + timedelta(days=90)
        ).count()
        
        return context


class MOUDetailView(LoginRequiredMixin, DetailView):
    model = MOU
    template_name = 'mous/mou_detail.html'
    context_object_name = 'mou'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Log activity
        log_activity(
            mou=obj,
            action='accessed',
            user=self.request.user,
            ip_address=get_client_ip(self.request)
        )
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activity_logs'] = self.object.activity_logs.all()[:20]
        context['share_links'] = self.object.share_links.filter(is_active=True)
        return context


class MOUCreateView(LoginRequiredMixin, CreateView):
    model = MOU
    form_class = MOUForm
    template_name = 'mous/mou_form.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Extract data from PDF if uploaded
        if form.instance.pdf_file:
            try:
                extracted_data = extract_pdf_data(form.instance.pdf_file.path)
                form.instance.clauses = extracted_data
                form.instance.save()
            except Exception as e:
                messages.warning(self.request, f"Could not extract data from PDF: {str(e)}")
        
        # Log activity
        log_activity(
            mou=form.instance,
            action='created',
            user=self.request.user,
            ip_address=get_client_ip(self.request)
        )
        
        messages.success(self.request, 'MOU created successfully!')
        return response
    
    def get_success_url(self):
        return reverse_lazy('mous:mou_detail', kwargs={'pk': self.object.pk})


class MOUUpdateView(LoginRequiredMixin, UpdateView):
    model = MOU
    form_class = MOUForm
    template_name = 'mous/mou_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Log activity
        log_activity(
            mou=form.instance,
            action='updated',
            user=self.request.user,
            ip_address=get_client_ip(self.request)
        )
        
        messages.success(self.request, 'MOU updated successfully!')
        return response
    
    def get_success_url(self):
        return reverse_lazy('mous:mou_detail', kwargs={'pk': self.object.pk})


@login_required
def generate_share_link(request, pk):
    """Generate a shareable link for external partners"""
    mou = get_object_or_404(MOU, pk=pk)
    
    if request.method == 'POST':
        # Create share link
        share_link = ShareLink.objects.create(
            mou=mou,
            created_by=request.user,
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        # Log activity
        log_activity(
            mou=mou,
            action='link_generated',
            user=request.user,
            ip_address=get_client_ip(request),
            description=f"Share link created with token {share_link.token}"
        )
        
        share_url = request.build_absolute_uri(
            reverse('mous:mou_sign', kwargs={'token': share_link.token})
        )
        
        return JsonResponse({
            'success': True,
            'share_url': share_url,
            'expires_at': share_link.expires_at.isoformat()
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def mou_sign_view(request, token):
    """Public view for external partners to sign MOUs"""
    share_link = get_object_or_404(ShareLink, token=token)
    
    if not share_link.is_valid:
        if share_link.is_expired:
            return render(request, 'mous/link_expired.html')
        else:
            return render(request, 'mous/link_invalid.html')
    
    # Increment access count
    share_link.access_count += 1
    share_link.save()
    
    # Log activity
    log_activity(
        mou=share_link.mou,
        action='link_accessed',
        ip_address=get_client_ip(request),
        description=f"Share link accessed via token {token}"
    )
    
    if request.method == 'POST':
        form = PartnerSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.share_link = share_link
            submission.ip_address = get_client_ip(request)
            submission.save()
            
            # Log activity
            log_activity(
                mou=share_link.mou,
                action='signed',
                user_name=submission.partner_name,
                user_email=submission.partner_email,
                ip_address=get_client_ip(request),
                description=f"MOU signed by {submission.partner_name}"
            )
            
            return render(request, 'mous/submission_success.html', {
                'submission': submission,
                'mou': share_link.mou
            })
    else:
        form = PartnerSubmissionForm()
    
    return render(request, 'mous/mou_sign.html', {
        'form': form,
        'mou': share_link.mou,
        'share_link': share_link
    })


@login_required
def approve_mou(request, pk):
    """Approve or reject an MOU"""
    mou = get_object_or_404(MOU, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            mou.status = 'approved'
            activity_action = 'approved'
            messages.success(request, 'MOU approved successfully!')
        elif action == 'reject':
            mou.status = 'draft'
            activity_action = 'rejected'
            messages.success(request, 'MOU rejected.')
        else:
            messages.error(request, 'Invalid action.')
            return redirect('mous:mou_detail', pk=pk)
        
        mou.save()
        
        # Log activity
        log_activity(
            mou=mou,
            action=activity_action,
            user=request.user,
            ip_address=get_client_ip(request)
        )
    
    return redirect('mous:mou_detail', pk=pk)


@login_required
def mou_submissions(request, pk):
    """View submissions for a specific MOU"""
    mou = get_object_or_404(MOU, pk=pk)
    submissions = PartnerSubmission.objects.filter(share_link__mou=mou)
    
    return render(request, 'mous/mou_submissions.html', {
        'mou': mou,
        'submissions': submissions
    })


@login_required
def dashboard(request):
    """Dashboard with statistics and recent activities"""
    context = {
        'total_mous': MOU.objects.count(),
        'active_mous': MOU.objects.filter(status='approved').count(),
        'pending_mous': MOU.objects.filter(status='pending').count(),
        'expired_mous': MOU.objects.filter(status='expired').count(),
        'expiring_soon': MOU.objects.filter(
            status='approved',
            expiry_date__lte=datetime.now().date() + timedelta(days=90)
        ),
        'recent_activities': ActivityLog.objects.all()[:10],
        'recent_mous': MOU.objects.all()[:5],
    }
    
    return render(request, 'mous/dashboard.html', context)


@login_required
@xframe_options_sameorigin
def view_pdf(request, pk):
    """Serve PDF files with proper headers for viewing"""
    mou = get_object_or_404(MOU, pk=pk)
    
    if not mou.pdf_file:
        raise Http404("PDF file not found")
    
    try:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{mou.title}.pdf"'
        
        # Add cache headers for better performance
        response['Cache-Control'] = 'private, max-age=3600'
        
        with open(mou.pdf_file.path, 'rb') as pdf_file:
            response.write(pdf_file.read())
        
        # Log activity
        log_activity(
            mou=mou,
            action='accessed',
            user=request.user,
            ip_address=get_client_ip(request),
            description="PDF viewed"
        )
        
        return response
        
    except FileNotFoundError:
        raise Http404("PDF file not found on disk")
