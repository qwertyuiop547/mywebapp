from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import models
from django.http import JsonResponse
from django.utils import timezone
from .models import Announcement, AnnouncementNotification
from notifications.models import Notification
from .forms import AnnouncementForm, AnnouncementFilterForm

def is_official(user):
    """Check if user is secretary or chairman"""
    return user.is_authenticated and user.role in ['secretary', 'chairman']

def announcement_list(request):
    """Public list of active and approved announcements"""
    announcements = Announcement.objects.filter(
        is_published=True,
        approval_status='approved',  # Only show approved announcements
        publish_date__lte=timezone.now()
    ).exclude(
        expiry_date__lt=timezone.now()
    )
    
    # Filter form
    filter_form = AnnouncementFilterForm(request.GET)
    
    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search')
        category = filter_form.cleaned_data.get('category')
        priority = filter_form.cleaned_data.get('priority')
        
        if search:
            announcements = announcements.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        if category:
            announcements = announcements.filter(category=category)
            
        if priority:
            announcements = announcements.filter(priority=priority)
    
    # Pagination
    paginator = Paginator(announcements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'announcements': page_obj,
        'filter_form': filter_form,
        'page_obj': page_obj,
    }
    return render(request, 'announcements/announcement_list.html', context)

def announcement_detail(request, pk):
    """Detailed view of announcement"""
    announcement = get_object_or_404(Announcement, pk=pk)
    
    # Check if announcement is accessible
    if not announcement.is_active and not is_official(request.user):
        messages.error(request, 'This announcement is not currently available.')
        return redirect('announcements:announcement_list')
    
    # Increment view count
    announcement.increment_views()
    
    context = {
        'announcement': announcement,
    }
    return render(request, 'announcements/announcement_detail.html', context)

@login_required
@user_passes_test(is_official)
def create_announcement(request):
    """Create new announcement (secretary/chairman only)"""
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            # Set default category and priority for simplified announcements
            announcement.category = 'general'
            announcement.priority = 'medium'
            
            # Approval workflow: Chairman can auto-approve, Secretary needs approval
            if request.user.role == 'chairman':
                announcement.approval_status = 'approved'
                announcement.approved_by = request.user
                announcement.approved_at = timezone.now()
            else:  # Secretary
                announcement.approval_status = 'pending'
            
            announcement.save()
            
            # Create notification for the creator
            create_announcement_notification(
                announcement=announcement,
                notification_type='created',
                recipient=request.user
            )
            
            # Notify residents only if already approved (chairman created)
            if announcement.approval_status == 'approved':
                notify_all_residents_about_announcement(announcement)
                messages.success(request, f'Visual announcement "{announcement.title}" has been created and published!')
            else:
                # Notify chairman for approval if secretary created
                notify_chairman_for_approval(announcement)
                messages.success(request, f'Visual announcement "{announcement.title}" has been created and sent for approval!')
            
            return redirect('announcements:announcement_detail', pk=announcement.pk)
    else:
        form = AnnouncementForm()
    
    context = {
        'form': form,
        'title': 'Gumawa ng Visual Announcement'
    }
    return render(request, 'announcements/announcement_form.html', context)

@login_required
@user_passes_test(is_official)
def edit_announcement(request, pk):
    """Edit existing announcement (secretary/chairman only)"""
    announcement = get_object_or_404(Announcement, pk=pk)
    
    # Only creator or chairman can edit
    if announcement.created_by != request.user and request.user.role != 'chairman':
        messages.error(request, 'You do not have permission to edit this announcement.')
        return redirect('announcements:announcement_detail', pk=pk)
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            announcement = form.save()
            
            # Create notification for update
            create_announcement_notification(
                announcement=announcement,
                notification_type='updated',
                recipient=announcement.created_by
            )
            
            messages.success(request, f'Visual announcement "{announcement.title}" has been updated!')
            return redirect('announcements:announcement_detail', pk=announcement.pk)
    else:
        form = AnnouncementForm(instance=announcement)
    
    context = {
        'form': form,
        'announcement': announcement,
        'title': 'Edit Announcement'
    }
    return render(request, 'announcements/announcement_form.html', context)

@login_required
@user_passes_test(is_official)
def manage_announcements(request):
    """Management view for announcements (secretary/chairman only)"""
    announcements = Announcement.objects.all()
    
    # Filter by creator for secretary
    if request.user.role == 'secretary':
        announcements = announcements.filter(created_by=request.user)
    
    # Apply filters
    filter_form = AnnouncementFilterForm(request.GET)
    
    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search')
        category = filter_form.cleaned_data.get('category')
        priority = filter_form.cleaned_data.get('priority')
        is_active = filter_form.cleaned_data.get('is_active')
        
        if search:
            announcements = announcements.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        if category:
            announcements = announcements.filter(category=category)
            
        if priority:
            announcements = announcements.filter(priority=priority)
            
        if is_active:
            now = timezone.now()
            announcements = announcements.filter(
                is_published=True,
                publish_date__lte=now
            ).exclude(expiry_date__lt=now)
    
    # Pagination
    paginator = Paginator(announcements, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'announcements': page_obj,
        'filter_form': filter_form,
        'page_obj': page_obj,
    }
    return render(request, 'announcements/manage_announcements.html', context)

@login_required
def my_notifications(request):
    """View user's announcement notifications"""
    notifications = AnnouncementNotification.objects.filter(recipient=request.user)
    
    # Mark as read when viewed
    notifications.filter(is_read=False).update(is_read=True, read_at=timezone.now())
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'announcements/notifications.html', context)

@login_required
def pending_approvals(request):
    """View for chairman to see pending announcements (chairman only)"""
    if request.user.role != 'chairman':
        messages.error(request, 'Only the chairman can access approval management.')
        return redirect('announcements:announcement_list')
    
    pending_announcements = Announcement.objects.filter(approval_status='pending').order_by('-created_at')
    
    context = {
        'pending_announcements': pending_announcements,
    }
    return render(request, 'announcements/pending_approvals.html', context)

@login_required
def approve_announcement(request, pk):
    """Approve an announcement (chairman only)"""
    if request.user.role != 'chairman':
        messages.error(request, 'Only the chairman can approve announcements.')
        return redirect('announcements:announcement_list')
    
    announcement = get_object_or_404(Announcement, pk=pk)
    
    if request.method == 'POST':
        announcement.approve(request.user)
        
        # Notify creator about approval
        create_announcement_notification(
            announcement=announcement,
            notification_type='approved',
            recipient=announcement.created_by
        )
        
        # Notify all residents about the approved announcement
        notify_all_residents_about_announcement(announcement)
        
        messages.success(request, f'Announcement "{announcement.title}" has been approved and published!')
        return redirect('announcements:pending_approvals')
    
    context = {
        'announcement': announcement,
    }
    return render(request, 'announcements/approve_announcement.html', context)

@login_required
def reject_announcement(request, pk):
    """Reject an announcement (chairman only)"""
    if request.user.role != 'chairman':
        messages.error(request, 'Only the chairman can reject announcements.')
        return redirect('announcements:announcement_list')
    
    announcement = get_object_or_404(Announcement, pk=pk)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        announcement.reject(request.user, reason)
        
        # Notify creator about rejection
        create_announcement_notification(
            announcement=announcement,
            notification_type='rejected',
            recipient=announcement.created_by
        )
        
        messages.success(request, f'Announcement "{announcement.title}" has been rejected.')
        return redirect('announcements:pending_approvals')
    
    context = {
        'announcement': announcement,
    }
    return render(request, 'announcements/reject_announcement.html', context)

def create_announcement_notification(announcement, notification_type, recipient):
    """Helper function to create announcement notifications"""
    
    notification_messages = {
        'created': {
            'title': f'Announcement Created: {announcement.title}',
            'message': f'Your announcement "{announcement.title}" has been created successfully.'
        },
        'updated': {
            'title': f'Announcement Updated: {announcement.title}',
            'message': f'Your announcement "{announcement.title}" has been updated.'
        },
        'published': {
            'title': f'Announcement Published: {announcement.title}',
            'message': f'Your announcement "{announcement.title}" is now live and visible to residents.'
        },
        'expired': {
            'title': f'Announcement Expired: {announcement.title}',
            'message': f'Your announcement "{announcement.title}" has expired and is no longer visible.'
        },
        'approved': {
            'title': f'Announcement Approved: {announcement.title}',
            'message': f'Your announcement "{announcement.title}" has been approved by the Chairman and is now visible to residents!'
        },
        'rejected': {
            'title': f'Announcement Rejected: {announcement.title}',
            'message': f'Your announcement "{announcement.title}" was rejected by the Chairman. Reason: {announcement.rejection_reason}'
        }
    }
    
    notification_data = notification_messages.get(notification_type, {
        'title': f'Announcement Notification: {announcement.title}',
        'message': f'There has been an update to your announcement "{announcement.title}".'
    })
    
    AnnouncementNotification.objects.create(
        announcement=announcement,
        notification_type=notification_type,
        recipient=recipient,
        title=notification_data['title'],
        message=notification_data['message']
    )

def notify_all_residents_about_announcement(announcement):
    """Notify all residents about new announcement using main notification system"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Only send notifications if announcement is published
    if not announcement.is_published:
        return
    
    # Get all residents (users with role='resident' or no specific role)
    residents = User.objects.filter(
        models.Q(role='resident') | models.Q(role__isnull=True) | models.Q(role='')
    ).exclude(id=announcement.created_by.id)  # Don't notify the creator
    
    # Create notifications using the main notification system
    notifications_to_create = []
    for resident in residents:
        notifications_to_create.append(
            Notification(
                recipient=resident,
                notification_type='system_announcement',
                title=f'📢 Bagong Announcement: {announcement.title}',
                message=f'May bagong visual announcement mula sa barangay: "{announcement.title}". Tingnan mo na ang larawan!',
                priority='medium',
                related_announcement=announcement
            )
        )
    
    # Bulk create for better performance
    if notifications_to_create:
        Notification.objects.bulk_create(notifications_to_create)

def notify_chairman_for_approval(announcement):
    """Notify chairman that an announcement needs approval"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Find the chairman
    chairman = User.objects.filter(role='chairman').first()
    if chairman:
        Notification.objects.create(
            recipient=chairman,
            notification_type='system_announcement',
            title=f'📋 Announcement Needs Approval: {announcement.title}',
            message=f'Secretary {announcement.created_by.get_full_name()} created an announcement that needs your approval: "{announcement.title}"',
            priority='high',
            related_announcement=announcement
        )

@login_required
@user_passes_test(is_official)
def delete_announcement(request, pk):
    """Delete an announcement (creator or chairman only)"""
    announcement = get_object_or_404(Announcement, pk=pk)
    
    # Only creator or chairman can delete
    if announcement.created_by != request.user and request.user.role != 'chairman':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'You do not have permission to delete this announcement.'})
        messages.error(request, 'You do not have permission to delete this announcement.')
        return redirect('announcements:manage_announcements')
    
    if request.method == 'POST':
        announcement_title = announcement.title
        announcement.delete()
        
        # Handle AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Announcement "{announcement_title}" has been deleted successfully.'
            })
        
        messages.success(request, f'Announcement "{announcement_title}" has been deleted successfully.')
        return redirect('announcements:manage_announcements')
    
    # For GET requests, redirect to manage page
    return redirect('announcements:manage_announcements')
