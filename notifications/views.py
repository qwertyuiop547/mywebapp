from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Notification, NotificationPreference
from .utils import create_notification

@login_required
def notification_list(request):
    """List all notifications for the current user"""
    notifications = request.user.notifications.all()
    
    # Mark as read if requested
    if request.GET.get('mark_all_read'):
        notifications.filter(is_read=False).update(is_read=True, read_at=timezone.now())
        messages.success(request, "All notifications marked as read.")
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'unread_count': notifications.filter(is_read=False).count(),
    }
    
    return render(request, 'notifications/notification_list.html', context)

@login_required
def notification_detail(request, notification_id):
    """Show a single notification with full details and mark it as read."""
    try:
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    except Http404:
        # If notification doesn't exist, redirect to notifications list with message
        messages.info(request, "This notification has been deleted or no longer exists.")
        return redirect('notifications:notification_list')
    
    # Mark as read when opened
    if not notification.is_read:
        notification.mark_as_read()
    
    context = {
        'notification': notification,
        'related_complaint': notification.related_complaint,
    }
    return render(request, 'notifications/notification_detail.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications:notification_list')

@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current user"""
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True, read_at=timezone.now())
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        messages.success(request, "All notifications marked as read.")
    
    return redirect('notifications:notification_list')

@login_required
def notification_preferences(request):
    """Manage notification preferences"""
    preferences, created = NotificationPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update preferences
        preferences.email_complaint_updates = request.POST.get('email_complaint_updates') == 'on'
        preferences.email_feedback_responses = request.POST.get('email_feedback_responses') == 'on'
        preferences.email_system_announcements = request.POST.get('email_system_announcements') == 'on'
        preferences.inapp_complaint_updates = request.POST.get('inapp_complaint_updates') == 'on'
        preferences.inapp_feedback_responses = request.POST.get('inapp_feedback_responses') == 'on'
        preferences.inapp_system_announcements = request.POST.get('inapp_system_announcements') == 'on'
        preferences.save()
        
        messages.success(request, "Notification preferences updated successfully!")
    
    return render(request, 'notifications/preferences.html', {'preferences': preferences})

@login_required
def get_unread_notifications_count(request):
    """API endpoint to get unread notification count"""
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'unread_count': count})

@login_required
def get_recent_notifications(request):
    """API endpoint to get recent notifications"""
    notifications = request.user.notifications.all()[:10]  # Get all recent, not just unread
    
    data = []
    for notification in notifications:
        data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'priority': notification.priority,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'notification_type': notification.notification_type,
            'link': notification.get_link,
        })
    
    return JsonResponse(data, safe=False)

@login_required
def delete_notification(request, notification_id):
    """Delete a specific notification"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    
    if request.method == 'POST':
        notification_title = notification.title
        notification.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': f'Notification "{notification_title}" deleted successfully.'
            })
        
        messages.success(request, f'Notification "{notification_title}" deleted successfully.')
        return redirect('notifications:notification_list')
    
    # For GET requests, redirect to list
    return redirect('notifications:notification_list')

@login_required
def delete_all_notifications(request):
    """Delete all notifications for the current user"""
    if request.method == 'POST':
        count = request.user.notifications.count()
        request.user.notifications.all().delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{count} notification{"s" if count != 1 else ""} deleted successfully.'
            })
        
        messages.success(request, f'{count} notification{"s" if count != 1 else ""} deleted successfully.')
    
    return redirect('notifications:notification_list')