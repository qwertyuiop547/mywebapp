from .models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()

def create_notification(recipient, notification_type, title, message, priority='medium', 
                       related_complaint=None, related_feedback=None):
    """
    Create a new notification for a user
    """
    # Check user's notification preferences
    preferences = getattr(recipient, 'notification_preferences', None)
    
    # Determine if user wants this type of notification
    should_create = True
    if preferences:
        if notification_type.startswith('complaint') and not preferences.inapp_complaint_updates:
            should_create = False
        elif notification_type.startswith('feedback') and not preferences.inapp_feedback_responses:
            should_create = False
        elif notification_type == 'system_announcement' and not preferences.inapp_system_announcements:
            should_create = False
    
    if should_create:
        notification = Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            related_complaint=related_complaint,
            related_feedback=related_feedback
        )
        return notification
    
    return None

def create_bulk_notification(users, notification_type, title, message, priority='medium'):
    """
    Create notifications for multiple users
    """
    notifications = []
    for user in users:
        notification = create_notification(
            recipient=user,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority
        )
        if notification:
            notifications.append(notification)
    
    return notifications

def notify_complaint_created(complaint):
    """Notify relevant staff when a new complaint is created"""
    staff_users = User.objects.filter(
        role__in=['secretary', 'chairman'], 
        is_approved=True
    )
    
    title = f"New Complaint: {complaint.title}"
    message = f"{complaint.complainant.get_full_name()} submitted a new {complaint.category.name} complaint."
    
    return create_bulk_notification(
        users=staff_users,
        notification_type='complaint_created',
        title=title,
        message=message,
        priority='medium'
    )

def notify_complaint_updated(complaint):
    """Notify complainant when their complaint is updated"""
    if complaint.complainant:
        title = f"Complaint Update: {complaint.title}"
        message = f"Your complaint status has been updated to: {complaint.get_status_display()}"
        
        return create_notification(
            recipient=complaint.complainant,
            notification_type='complaint_updated',
            title=title,
            message=message,
            priority='medium',
            related_complaint=complaint
        )

def notify_complaint_rejected(complaint):
    """Notify complainant when their complaint is rejected"""
    if complaint.complainant:
        title = f"Complaint Rejected: {complaint.title}"
        message = f"Your complaint has been reviewed and rejected by the Barangay Secretary. Reason: {complaint.rejection_reason[:100]}{'...' if len(complaint.rejection_reason) > 100 else ''}"
        
        return create_notification(
            recipient=complaint.complainant,
            notification_type='complaint_rejected',
            title=title,
            message=message,
            priority='medium',
            related_complaint=complaint
        )

def notify_feedback_response(feedback):
    """Notify user when admin responds to their feedback"""
    if feedback.user and feedback.admin_response:
        title = f"Response to Your Feedback: {feedback.title}"
        message = "An administrator has responded to your feedback."
        
        return create_notification(
            recipient=feedback.user,
            notification_type='feedback_received',
            title=title,
            message=message,
            priority='medium',
            related_feedback=feedback
        )

def notify_user_approved(user):
    """Notify user when their account is approved"""
    title = "Account Approved"
    message = "Your account has been approved! You can now access the Barangay Portal."
    
    return create_notification(
        recipient=user,
        notification_type='user_approved',
        title=title,
        message=message,
        priority='high'
    )

def create_system_announcement(title, message, priority='medium', target_roles=None):
    """Create system-wide announcement"""
    if target_roles:
        users = User.objects.filter(role__in=target_roles, is_approved=True)
    else:
        users = User.objects.filter(is_approved=True)
    
    return create_bulk_notification(
        users=users,
        notification_type='system_announcement',
        title=title,
        message=message,
        priority=priority
    )