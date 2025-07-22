from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'mous'

def redirect_to_mou_list(request):
    """Redirect root URL to MOU list"""
    return redirect('mous:mou_list')

urlpatterns = [
    # Redirect root to MOU list
    path('', redirect_to_mou_list, name='dashboard'),
    
    # MOU CRUD operations
    path('mous/', views.MOUListView.as_view(), name='mou_list'),
    path('mous/create/', views.MOUCreateView.as_view(), name='mou_create'),
    path('mous/<int:pk>/', views.MOUDetailView.as_view(), name='mou_detail'),
    path('mous/<int:pk>/edit/', views.MOUUpdateView.as_view(), name='mou_edit'),
    
    # Dashboard (separate URL if needed)
    path('dashboard/', views.dashboard, name='dashboard_view'),
    
    # MOU Actions
    path('mous/<int:pk>/approve/', views.approve_mou, name='mou_approve'),
    path('mous/<int:pk>/generate-link/', views.generate_share_link, name='generate_share_link'),
    path('mous/<int:pk>/submissions/', views.mou_submissions, name='mou_submissions'),
    path('mous/<int:pk>/pdf/', views.view_pdf, name='view_pdf'),
    
    # AI Analysis API
    path('api/mous/<int:pk>/analyze/', views.trigger_ai_analysis, name='trigger_ai_analysis'),
    path('api/bulk-analyze/', views.bulk_ai_analysis, name='bulk_ai_analysis'),
    
    # Public signing interface
    path('sign/<uuid:token>/', views.mou_sign_view, name='mou_sign'),
]
