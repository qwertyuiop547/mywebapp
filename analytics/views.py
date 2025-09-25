from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta, date
from calendar import monthrange
import json

from complaints.models import Complaint, ComplaintCategory
from feedback.models import Feedback
from accounts.models import User


@login_required
def analytics_overview(request):
    """Main analytics dashboard with overview statistics."""
    if not request.user.can_manage_complaints():
        return render(request, '403.html')
    
    # Date range filtering
    days = int(request.GET.get('days', 30))
    start_date = timezone.now().date() - timedelta(days=days)
    
    # Basic statistics
    stats = {
        'total_complaints': Complaint.objects.count(),
        'total_feedback': Feedback.objects.count(),
        'total_residents': User.objects.filter(role='resident', is_approved=True).count(),
        'pending_approvals': User.objects.filter(role='resident', is_approved=False).count(),
    }
    
    # Complaint statistics by status
    complaint_stats = Complaint.objects.aggregate(
        pending=Count('id', filter=Q(status='pending')),
        in_progress=Count('id', filter=Q(status='in_progress')),
        resolved=Count('id', filter=Q(status='resolved')),
        closed=Count('id', filter=Q(status='closed')),
    )
    
    # Recent activity
    recent_complaints = Complaint.objects.filter(
        created_at__date__gte=start_date
    ).count()
    
    recent_feedback = Feedback.objects.filter(
        created_at__date__gte=start_date
    ).count()
    
    # Category distribution
    category_stats = list(
        ComplaintCategory.objects.annotate(
            complaint_count=Count('complaint')
        ).values('name', 'complaint_count')
        .order_by('-complaint_count')
    )
    
    # Monthly trends (last 6 months)
    monthly_data = []
    for i in range(6):
        month_date = (timezone.now().date() - timedelta(days=i*30)).replace(day=1)
        month_complaints = Complaint.objects.filter(
            created_at__year=month_date.year,
            created_at__month=month_date.month
        ).count()
        monthly_data.append({
            'month': month_date.strftime('%B %Y'),
            'complaints': month_complaints
        })
    
    monthly_data.reverse()  # Show chronologically
    
    # Priority distribution
    priority_stats = Complaint.objects.aggregate(
        low=Count('id', filter=Q(priority='low')),
        medium=Count('id', filter=Q(priority='medium')),
        high=Count('id', filter=Q(priority='high')),
        urgent=Count('id', filter=Q(priority='urgent')),
    )
    
    # Average resolution time
    resolved_complaints = Complaint.objects.filter(
        status__in=['resolved', 'closed'],
        resolution_date__isnull=False
    )
    
    avg_resolution_days = 0
    if resolved_complaints.exists():
        total_days = sum([
            (complaint.resolution_date.date() - complaint.created_at.date()).days
            for complaint in resolved_complaints
            if complaint.resolution_date
        ])
        avg_resolution_days = total_days / resolved_complaints.count()
    
    # Top complainants
    top_complainants = list(
        User.objects.filter(
            complaint__isnull=False,
            role='resident'
        ).annotate(
            complaint_count=Count('complaint')
        ).values(
            'first_name', 'last_name', 'username', 'complaint_count'
        ).order_by('-complaint_count')[:10]
    )
    
    # Feedback statistics
    feedback_stats = Feedback.objects.aggregate(
        total=Count('id'),
        with_response=Count('id', filter=Q(admin_response__isnull=False)),
        avg_rating=Avg('rating') or 0,
    )
    
    context = {
        'stats': stats,
        'complaint_stats': complaint_stats,
        'recent_complaints': recent_complaints,
        'recent_feedback': recent_feedback,
        'category_stats': category_stats,
        'monthly_data': json.dumps(monthly_data),
        'priority_stats': priority_stats,
        'avg_resolution_days': round(avg_resolution_days, 1),
        'top_complainants': top_complainants,
        'feedback_stats': feedback_stats,
        'selected_days': days,
    }
    
    return render(request, 'analytics/overview.html', context)


@login_required
def analytics_complaints(request):
    """Detailed complaints analytics."""
    if not request.user.can_manage_complaints():
        return render(request, '403.html')
    
    # Time-based analysis
    daily_data = []
    for i in range(30):
        day = timezone.now().date() - timedelta(days=i)
        count = Complaint.objects.filter(created_at__date=day).count()
        daily_data.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    daily_data.reverse()
    
    # Status trends over time
    status_trends = []
    for i in range(12):  # Last 12 weeks
        week_start = timezone.now().date() - timedelta(weeks=i+1)
        week_end = timezone.now().date() - timedelta(weeks=i)
        
        week_stats = Complaint.objects.filter(
            created_at__date__range=[week_start, week_end]
        ).aggregate(
            pending=Count('id', filter=Q(status='pending')),
            in_progress=Count('id', filter=Q(status='in_progress')),
            resolved=Count('id', filter=Q(status='resolved')),
        )
        
        status_trends.append({
            'week': f"Week of {week_start.strftime('%m/%d')}",
            **week_stats
        })
    
    status_trends.reverse()
    
    # Category performance
    category_performance = list(
        ComplaintCategory.objects.annotate(
            total_complaints=Count('complaint'),
            resolved_complaints=Count('complaint', filter=Q(complaint__status='resolved')),
        ).values(
            'name', 'total_complaints', 'resolved_complaints'
        ).order_by('-total_complaints')
    )
    
    # Calculate resolution rates
    for cat in category_performance:
        if cat['total_complaints'] > 0:
            cat['resolution_rate'] = (cat['resolved_complaints'] / cat['total_complaints']) * 100
        else:
            cat['resolution_rate'] = 0
    
    context = {
        'daily_data': json.dumps(daily_data),
        'status_trends': json.dumps(status_trends),
        'category_performance': category_performance,
    }
    
    return render(request, 'analytics/complaints.html', context)


@login_required
def analytics_feedback(request):
    """Detailed feedback analytics."""
    if not request.user.can_manage_complaints():
        return render(request, '403.html')
    
    # Rating distribution
    rating_distribution = []
    for i in range(1, 6):
        count = Feedback.objects.filter(rating=i).count()
        rating_distribution.append({
            'rating': i,
            'count': count
        })
    
    # Monthly feedback trends
    monthly_feedback = []
    for i in range(6):
        month_date = (timezone.now().date() - timedelta(days=i*30)).replace(day=1)
        month_data = Feedback.objects.filter(
            created_at__year=month_date.year,
            created_at__month=month_date.month
        ).aggregate(
            total=Count('id'),
            avg_rating=Avg('rating') or 0
        )
        
        monthly_feedback.append({
            'month': month_date.strftime('%B %Y'),
            'total': month_data['total'],
            'avg_rating': round(month_data['avg_rating'], 1)
        })
    
    monthly_feedback.reverse()
    
    # Category-wise feedback
    feedback_categories = list(
        Feedback.objects.values('category').annotate(
            count=Count('id'),
            avg_rating=Avg('rating')
        ).order_by('-count')
    )
    
    # Response rate analysis
    response_stats = Feedback.objects.aggregate(
        total_feedback=Count('id'),
        with_response=Count('id', filter=Q(admin_response__isnull=False)),
        without_response=Count('id', filter=Q(admin_response__isnull=True))
    )
    
    if response_stats['total_feedback'] > 0:
        response_stats['response_rate'] = (
            response_stats['with_response'] / response_stats['total_feedback']
        ) * 100
    else:
        response_stats['response_rate'] = 0
    
    context = {
        'rating_distribution': json.dumps(rating_distribution),
        'monthly_feedback': json.dumps(monthly_feedback),
        'feedback_categories': feedback_categories,
        'response_stats': response_stats,
    }
    
    return render(request, 'analytics/feedback.html', context)


@login_required
def analytics_export(request):
    """Export analytics data as JSON."""
    if not request.user.can_manage_complaints():
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    export_type = request.GET.get('type', 'overview')
    
    if export_type == 'complaints':
        data = list(
            Complaint.objects.select_related(
                'category', 'complainant', 'assigned_to'
            ).values(
                'id', 'title', 'status', 'priority', 'created_at',
                'category__name', 'complainant__username',
                'assigned_to__username', 'resolution_date'
            )
        )
    elif export_type == 'feedback':
        data = list(
            Feedback.objects.values(
                'id', 'rating', 'category', 'created_at',
                'is_anonymous', 'admin_response'
            )
        )
    else:  # overview
        data = {
            'complaints': list(Complaint.objects.values()),
            'feedback': list(Feedback.objects.values()),
            'users': list(User.objects.filter(role='resident').values(
                'id', 'username', 'first_name', 'last_name',
                'is_approved', 'date_joined'
            ))
        }
    
    # Convert dates to strings for JSON serialization
    def serialize_dates(obj):
        if isinstance(obj, (date, timezone.datetime)):
            return obj.isoformat()
        elif isinstance(obj, list):
            return [serialize_dates(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: serialize_dates(value) for key, value in obj.items()}
        return obj
    
    data = serialize_dates(data)
    
    response = JsonResponse(data, safe=False)
    response['Content-Disposition'] = f'attachment; filename="{export_type}_data.json"'
    return response