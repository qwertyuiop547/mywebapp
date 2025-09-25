from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import UserLoginHistory


def get_client_ip(request):
    """Get the client's IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in)
def create_login_history(sender, request, user, **kwargs):
    """Create login history entry when user logs in"""
    # Get client information
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    session_key = request.session.session_key
    
    # Create login history entry
    login_history = UserLoginHistory.objects.create(
        user=user,
        session_key=session_key,
        ip_address=ip_address,
        user_agent=user_agent,
        is_active=True
    )
    
    # Parse user agent information
    login_history.parse_user_agent()
    login_history.save()
    
    # Mark previous sessions as inactive for this user
    UserLoginHistory.objects.filter(
        user=user,
        is_active=True
    ).exclude(id=login_history.id).update(is_active=False)


@receiver(user_logged_out)
def update_logout_time(sender, request, user, **kwargs):
    """Update logout time when user logs out"""
    if user and hasattr(request, 'session'):
        session_key = request.session.session_key
        
        # Find the current active session and mark it as logged out
        UserLoginHistory.objects.filter(
            user=user,
            session_key=session_key,
            is_active=True,
            logout_time__isnull=True
        ).update(
            logout_time=timezone.now(),
            is_active=False
        )
