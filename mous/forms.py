from django import forms
from django.core.exceptions import ValidationError
from .models import MOU, PartnerSubmission
import os


class MOUForm(forms.ModelForm):
    class Meta:
        model = MOU
        fields = ['title', 'description', 'partner_name', 'partner_organization', 
                 'partner_contact', 'expiry_date', 'status', 'pdf_file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter MOU title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter description (optional)'
            }),
            'partner_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter partner name'
            }),
            'partner_organization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter partner organization'
            }),
            'partner_contact': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter partner email'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'pdf_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            })
        }

    def clean_pdf_file(self):
        pdf_file = self.cleaned_data.get('pdf_file')
        if pdf_file:
            # Check file extension
            ext = os.path.splitext(pdf_file.name)[1].lower()
            if ext != '.pdf':
                raise ValidationError('Only PDF files are allowed.')
            
            # Check file size (10MB limit)
            if pdf_file.size > 10 * 1024 * 1024:
                raise ValidationError('File size must be less than 10MB.')
        
        return pdf_file


class PartnerSubmissionForm(forms.ModelForm):
    signature_data = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = PartnerSubmission
        fields = ['partner_name', 'partner_organization', 'partner_email', 
                 'partner_phone', 'updated_pdf', 'notes', 'signature_data']
        widgets = {
            'partner_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name'
            }),
            'partner_organization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your organization name'
            }),
            'partner_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'partner_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your phone number (optional)'
            }),
            'updated_pdf': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any additional notes or comments (optional)'
            })
        }

    def clean_updated_pdf(self):
        pdf_file = self.cleaned_data.get('updated_pdf')
        if pdf_file:
            # Check file extension
            ext = os.path.splitext(pdf_file.name)[1].lower()
            if ext != '.pdf':
                raise ValidationError('Only PDF files are allowed.')
            
            # Check file size (10MB limit)
            if pdf_file.size > 10 * 1024 * 1024:
                raise ValidationError('File size must be less than 10MB.')
        
        return pdf_file


class MOUFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'All Statuses')] + list(MOU.STATUS_CHOICES)
    SORT_CHOICES = [
        ('-created_at', 'Newest First'),
        ('created_at', 'Oldest First'),
        ('title', 'Title A-Z'),
        ('-title', 'Title Z-A'),
        ('expiry_date', 'Expiry Date (Soon)'),
        ('-expiry_date', 'Expiry Date (Later)'),
        ('partner_name', 'Partner A-Z'),
        ('-partner_name', 'Partner Z-A'),
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search MOUs...'
        })
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='-created_at',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
