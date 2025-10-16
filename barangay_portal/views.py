from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from complaints.models import Complaint
from feedback.models import Feedback
from accounts.models import User
from announcements.models import Announcement
from django.db.models import Q
from datetime import datetime, timedelta

def home(request):
    """
    Home page view displaying barangay statistics and quick access features
    """
    # Get basic statistics
    total_residents = User.objects.filter(role='resident').count()
    total_complaints = Complaint.objects.count()
    resolved_complaints = Complaint.objects.filter(status='resolved').count()
    pending_complaints = Complaint.objects.filter(status='pending').count()
    total_feedback = Feedback.objects.count()
    
    # Recent activities (last 30 days)
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_complaints = Complaint.objects.filter(created_at__gte=thirty_days_ago).count()
    recent_feedback = Feedback.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # Calculate resolution rate
    resolution_rate = 0
    if total_complaints > 0:
        resolution_rate = round((resolved_complaints / total_complaints) * 100, 1)
    
    # Get recent approved and published announcements (show latest 6)
    announcements = Announcement.objects.filter(
        approval_status='approved',
        is_published=True
    ).order_by('-is_pinned', '-created_at')[:6]
    
    context = {
        'total_residents': total_residents,
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'pending_complaints': pending_complaints,
        'total_feedback': total_feedback,
        'recent_complaints': recent_complaints,
        'recent_feedback': recent_feedback,
        'resolution_rate': resolution_rate,
        'announcements': announcements,
    }
    
    return render(request, 'home.html', context)

@login_required
def quick_stats_api(request):
    """
    API endpoint for quick statistics (for AJAX updates)
    """
    stats = {
        'total_complaints': Complaint.objects.count(),
        'pending_complaints': Complaint.objects.filter(status='pending').count(),
        'resolved_complaints': Complaint.objects.filter(status='resolved').count(),
        'total_feedback': Feedback.objects.count(),
    }
    return JsonResponse(stats)