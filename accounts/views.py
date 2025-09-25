from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import User, UserVerificationDocument, BarangayArea, ResidencyValidation, UserLoginHistory
from .forms import UserRegistrationForm, UserProfileForm, UserLoginForm
import logging

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_approved = False  # Require approval by chairman
            
            # Save the profile photo
            profile_photo = form.cleaned_data.get('profile_photo')
            if profile_photo:
                user.profile_photo = profile_photo
            
            user.save()
            
            
            # Save verification document if uploaded
            verification_doc = form.cleaned_data.get('verification_documents')
            if verification_doc:
                UserVerificationDocument.objects.create(user=user, file=verification_doc)
            
            messages.success(request, 'Registration successful! Please wait for approval from the Barangay Chairman.')
            return redirect('accounts:wait_approval')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def wait_approval_view(request):
    """Display wait for approval page after registration"""
    return render(request, 'accounts/wait_approval.html')

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            user = User.objects.get(username=username)
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('dashboard:home')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def user_approval_list(request):
    if not request.user.can_approve_users():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:home')
    
    # Get statistics
    total_users = User.objects.filter(is_superuser=False).count()
    pending_users_count = User.objects.filter(is_approved=False, is_superuser=False).count()
    approved_users = User.objects.filter(is_approved=True, is_superuser=False).count()
    resident_users = User.objects.filter(is_approved=True, is_superuser=False, role='resident').count()
    
    # Get paginated pending users for the table
    pending_users = User.objects.filter(is_approved=False, is_superuser=False).order_by('-date_joined')
    paginator = Paginator(pending_users, 10)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    context = {
        'users': users,
        'user_list': users,  # Template expects 'user_list'
        'total_users': total_users,
        'pending_users_count': pending_users_count,
        'approved_users': approved_users,
        'resident_users': resident_users,
    }
    
    return render(request, 'accounts/user_approval.html', context)

@login_required
def approve_user(request, user_id):
    if not request.user.can_approve_users():
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('dashboard:home')
    
    user = get_object_or_404(User, id=user_id, is_approved=False)
    user.is_approved = True
    user.date_approved = timezone.now()
    user.save()
    
    messages.success(request, f'User {user.username} has been approved.')
    return redirect('accounts:user_approval')

@login_required
def reject_user(request, user_id):
    if not request.user.can_approve_users():
        # For AJAX request, return JSON error
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('dashboard:home')
    
    user = get_object_or_404(User, id=user_id, is_approved=False)
    username = user.username
    
    # Only allow POST for delete
    if request.method != 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Invalid method.'}, status=405)
        messages.error(request, 'Invalid request method.')
        return redirect('accounts:user_approval')

    user.delete()

    # If AJAX, return JSON to avoid page reload
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': f'User {username} has been rejected and deleted.', 'user_id': user_id})

    messages.warning(request, f'User {username} has been rejected and deleted.')
    return redirect('accounts:user_approval')

@login_required
def profile_view(request):
    """View and edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def view_user_documents(request, user_id):
    """View verification documents for a user"""
    if not request.user.can_approve_users():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:home')
    
    user = get_object_or_404(User, id=user_id)
    documents = UserVerificationDocument.objects.filter(user=user).order_by('-uploaded_at')
    
    context = {
        'user_account': user,
        'documents': documents,
    }
    return render(request, 'accounts/view_documents.html', context)

@login_required
def view_single_document(request, user_id, document_id):
    """View a single document with back navigation"""
    if not request.user.can_approve_users():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:home')
    
    user = get_object_or_404(User, id=user_id)
    document = get_object_or_404(UserVerificationDocument, id=document_id, user=user)
    
    context = {
        'user_account': user,
        'document': document,
    }
    return render(request, 'accounts/view_single_document.html', context)

@login_required
def view_user_profile(request, user_id):
    """View complete user profile with photo and details"""
    # Allow Chairman, Secretary, and the user themselves to view profile
    user_account = get_object_or_404(User, id=user_id)
    
    # Check permissions
    if not (request.user.can_approve_users() or request.user == user_account):
        messages.error(request, 'You do not have permission to view this profile.')
        return redirect('dashboard:home')
    
    documents = UserVerificationDocument.objects.filter(user=user_account).order_by('-uploaded_at')
    
    context = {
        'user_account': user_account,
        'documents': documents,
    }
    return render(request, 'accounts/view_user_profile.html', context)

@login_required
def delete_account_confirm(request):
    """Show confirmation page for account deletion"""
    # Only approved users can delete their accounts
    if not request.user.is_approved:
        messages.error(request, 'Only approved users can delete their accounts.')
        return redirect('dashboard:home')
    
    # Officials (Chairman/Secretary) cannot delete their accounts for security
    if request.user.role in ['chairman', 'secretary']:
        messages.error(request, 'Officials cannot delete their accounts for security purposes.')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/delete_account_confirm.html')

@login_required
def delete_own_account(request):
    """Delete user's own account after confirmation"""
    if request.method != 'POST':
        return redirect('accounts:delete_account_confirm')
    
    # Only approved users can delete their accounts
    if not request.user.is_approved:
        messages.error(request, 'Only approved users can delete their accounts.')
        return redirect('dashboard:home')
    
    # Officials (Chairman/Secretary) cannot delete their accounts for security
    if request.user.role in ['chairman', 'secretary']:
        messages.error(request, 'Officials cannot delete their accounts for security purposes.')
        return redirect('accounts:profile')
    
    # Check confirmation password
    password = request.POST.get('password')
    if not request.user.check_password(password):
        messages.error(request, 'Incorrect password. Account deletion cancelled.')
        return redirect('accounts:delete_account_confirm')
    
    # Store username for message before deletion
    username = request.user.username
    
    # Delete the user account
    try:
        request.user.delete()
        messages.success(request, f'Account "{username}" has been successfully deleted. Thank you for using Barangay Portal.')
        return redirect('home')
    except Exception as e:
        messages.error(request, 'An error occurred while deleting your account. Please try again or contact support.')
        return redirect('accounts:delete_account_confirm')


@login_required
def residents_map_view(request):
    """Display map with all resident locations"""
    if not request.user.can_approve_users():
        messages.error(request, 'Access denied. Only authorized personnel can view the residents map.')
        return redirect('dashboard:home')
    
    # Get all residents with location coordinates
    residents_with_location = User.objects.filter(
        role='resident', 
        is_approved=True,
        latitude__isnull=False,
        longitude__isnull=False
    ).exclude(
        latitude=0,
        longitude=0
    )
    
    context = {
        'residents': residents_with_location,
        'total_residents': residents_with_location.count(),
    }
    
    return render(request, 'accounts/residents_map.html', context)


# === CHAIRMAN USER MANAGEMENT VIEWS ===

@login_required
def user_management_list(request):
    """Chairman can view and manage all users in the barangay"""
    if not request.user.is_chairman():
        messages.error(request, 'Access denied. Only the Barangay Chairman can manage users.')
        return redirect('dashboard:home')
    
    # Get only residents (exclude barangay officials/employees)
    # Only show regular residents, not barangay officials
    users = User.objects.filter(role='resident').order_by('-date_joined')
    
    # Filter by search query
    search_query = request.GET.get('search', '').strip()
    if search_query:
        users = users.filter(
            models.Q(username__icontains=search_query) |
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(email__icontains=search_query)
        )
    
    # Since we're only showing residents, role filter is not needed
    # But we keep it for consistency (always resident anyway)
    role_filter = request.GET.get('role', '').strip()
    
    # Filter by status - this is the main filter for residents
    status_filter = request.GET.get('status', '').strip()
    if status_filter == 'active':
        users = users.filter(is_active=True, is_approved=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    elif status_filter == 'pending':
        users = users.filter(is_approved=False)
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Since we only show residents, we don't need role choices dropdown
    role_choices = [('resident', 'Resident')]
    
    # Calculate additional stats for modern template
    active_count = users.filter(is_active=True).count()
    total_residents = users.count()
    
    context = {
        'users': page_obj,
        'page_obj': page_obj,  # For modern template compatibility
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'role_choices': role_choices,
        'total_users': users.count(),
        'total_residents': total_residents,
        'active_count': active_count,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'accounts/user_management.html', context)


@login_required
def deactivate_user(request, user_id):
    """Chairman can deactivate/suspend a user account"""
    if not request.user.is_chairman():
        messages.error(request, 'Access denied. Only the Barangay Chairman can deactivate users.')
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        user_to_deactivate = get_object_or_404(User, id=user_id)
        
        # Since we only show residents now, additional check: ensure this is a resident
        if user_to_deactivate.role != 'resident':
            messages.error(request, 'You can only deactivate resident accounts.')
            return redirect('accounts:user_management')
        
        # Prevent deactivating self (though Chairman shouldn't show in resident list)
        if user_to_deactivate.id == request.user.id:
            messages.error(request, 'You cannot deactivate your own account.')
            return redirect('accounts:user_management')
        
        user_to_deactivate.is_active = False
        user_to_deactivate.save()
        
        # If AJAX request, return JSON response
        if request.headers.get('X-CSRFToken') and not request.headers.get('Accept', '').startswith('text/html'):
            return JsonResponse({
                'success': True,
                'message': f'Resident "{user_to_deactivate.get_full_name() or user_to_deactivate.username}" has been deactivated.',
                'action': 'deactivate'
            })
        
        messages.success(request, f'Resident "{user_to_deactivate.get_full_name() or user_to_deactivate.username}" has been deactivated.')
        return redirect('accounts:user_management')
    
    return redirect('accounts:user_management')


@login_required
def activate_user(request, user_id):
    """Chairman can reactivate a suspended user account"""
    if not request.user.is_chairman():
        messages.error(request, 'Access denied. Only the Barangay Chairman can activate users.')
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        user_to_activate = get_object_or_404(User, id=user_id)
        
        # Since we only show residents now, additional check: ensure this is a resident
        if user_to_activate.role != 'resident':
            messages.error(request, 'You can only activate resident accounts.')
            return redirect('accounts:user_management')
        
        user_to_activate.is_active = True
        # Also approve if not approved yet
        if not user_to_activate.is_approved:
            user_to_activate.is_approved = True
            user_to_activate.date_approved = timezone.now()
        
        user_to_activate.save()
        
        # If AJAX request, return JSON response
        if request.headers.get('X-CSRFToken') and not request.headers.get('Accept', '').startswith('text/html'):
            return JsonResponse({
                'success': True,
                'message': f'Resident "{user_to_activate.get_full_name() or user_to_activate.username}" has been activated.',
                'action': 'activate'
            })
        
        messages.success(request, f'Resident "{user_to_activate.get_full_name() or user_to_activate.username}" has been activated.')
        return redirect('accounts:user_management')
    
    return redirect('accounts:user_management')


@login_required
def delete_user_account(request, user_id):
    """Chairman can permanently delete a user account (use with extreme caution)"""
    if not request.user.is_chairman():
        messages.error(request, 'Access denied. Only the Barangay Chairman can delete user accounts.')
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        user_to_delete = get_object_or_404(User, id=user_id)
        
        # Since we only show residents now, additional check: ensure this is a resident
        if user_to_delete.role != 'resident':
            messages.error(request, 'You can only delete resident accounts.')
            return redirect('accounts:user_management')
        
        # Prevent deleting self (though Chairman shouldn't show in resident list)
        if user_to_delete.id == request.user.id:
            messages.error(request, 'You cannot delete your own account.')
            return redirect('accounts:user_management')
        
        username = user_to_delete.get_full_name() or user_to_delete.username
        user_to_delete.delete()
        
        # If AJAX request, return JSON response
        if request.headers.get('X-CSRFToken') and not request.headers.get('Accept', '').startswith('text/html'):
            return JsonResponse({
                'success': True,
                'message': f'Resident account "{username}" has been permanently deleted.',
                'action': 'delete'
            })
        
        messages.success(request, f'Resident account "{username}" has been permanently deleted.')
        return redirect('accounts:user_management')
    
    return redirect('accounts:user_management')


# === AUTOMATIC RESIDENCY VALIDATION VIEWS ===

@login_required
def validate_residency(request):
    """AJAX endpoint to validate user's residency status"""
    if request.method == 'POST':
        try:
            # Perform validation
            validation = auto_validate_residency(request.user)
            feedback = get_validation_feedback(request.user)
            
            return JsonResponse({
                'success': True,
                'validation': {
                    'location_status': validation.location_status,
                    'address_status': validation.address_status,
                    'score': validation.auto_validation_score,
                    'overall_status': validation.get_overall_status(),
                    'notes': validation.validation_notes,
                    'feedback': feedback,
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def get_validation_status(request):
    """Get current validation status for a user"""
    feedback = get_validation_feedback(request.user)
    
    try:
        validation = request.user.residency_validation
        return JsonResponse({
            'success': True,
            'has_validation': True,
            'validation': {
                'location_status': validation.location_status,
                'address_status': validation.address_status,
                'score': validation.auto_validation_score,
                'overall_status': validation.get_overall_status(),
                'notes': validation.validation_notes.split('\n') if validation.validation_notes else [],
                'last_validated': validation.last_validated.isoformat(),
            },
            'feedback': feedback,
        })
    except ResidencyValidation.DoesNotExist:
        return JsonResponse({
            'success': True,
            'has_validation': False,
            'feedback': feedback,
        })


# === LOGIN HISTORY VIEWS ===

@login_required
def login_history_view(request):
    """View login history - role-based access control"""
    user = request.user
    
    # Check permissions
    if not user.can_view_all_login_history() and not user.can_view_user_login_history(user):
        messages.error(request, 'Access denied. You do not have permission to view login history.')
        return redirect('dashboard:home')
    
    # Get search parameters
    search_user = request.GET.get('user', '')
    search_ip = request.GET.get('ip', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    device_type = request.GET.get('device_type', '')
    
    # Base queryset - depends on user permissions
    if user.can_view_all_login_history():
        # Secretary/Chairman can see all login history
        login_history = UserLoginHistory.objects.select_related('user').all()
        show_all_users = True
    else:
        # Regular users can only see their own history
        login_history = UserLoginHistory.objects.filter(user=user)
        show_all_users = False
    
    # Apply filters
    if search_user and show_all_users:
        login_history = login_history.filter(
            Q(user__username__icontains=search_user) |
            Q(user__first_name__icontains=search_user) |
            Q(user__last_name__icontains=search_user) |
            Q(user__email__icontains=search_user)
        )
    
    if search_ip:
        login_history = login_history.filter(ip_address__icontains=search_ip)
    
    if date_from:
        login_history = login_history.filter(login_time__date__gte=date_from)
    
    if date_to:
        login_history = login_history.filter(login_time__date__lte=date_to)
    
    if device_type:
        login_history = login_history.filter(device_type=device_type)
    
    # Get statistics
    stats = {
        'total_sessions': login_history.count(),
        'active_sessions': login_history.filter(is_active=True).count(),
        'desktop_sessions': login_history.filter(device_type='desktop').count(),
        'mobile_sessions': login_history.filter(device_type='mobile').count(),
        'tablet_sessions': login_history.filter(device_type='tablet').count(),
        'suspicious_sessions': login_history.filter(is_suspicious=True).count(),
    }
    
    # Pagination
    paginator = Paginator(login_history.order_by('-login_time'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all users for filter dropdown (if admin)
    all_users = []
    if show_all_users:
        all_users = User.objects.filter(is_approved=True).order_by('username')
    
    context = {
        'login_history': page_obj,
        'stats': stats,
        'show_all_users': show_all_users,
        'all_users': all_users,
        'search_user': search_user,
        'search_ip': search_ip,
        'date_from': date_from,
        'date_to': date_to,
        'device_type': device_type,
        'device_types': [
            ('desktop', 'Desktop'),
            ('mobile', 'Mobile'),
            ('tablet', 'Tablet'),
        ],
    }
    
    return render(request, 'accounts/login_history.html', context)


@login_required
def user_login_history_view(request, user_id):
    """View specific user's login history"""
    target_user = get_object_or_404(User, id=user_id)
    
    # Check permissions
    if not request.user.can_view_user_login_history(target_user):
        messages.error(request, 'Access denied. You cannot view this user\'s login history.')
        return redirect('dashboard:home')
    
    # Get login history for this user
    login_history = UserLoginHistory.objects.filter(user=target_user).order_by('-login_time')
    
    # Get statistics for this user
    stats = {
        'total_sessions': login_history.count(),
        'active_sessions': login_history.filter(is_active=True).count(),
        'desktop_sessions': login_history.filter(device_type='desktop').count(),
        'mobile_sessions': login_history.filter(device_type='mobile').count(),
        'tablet_sessions': login_history.filter(device_type='tablet').count(),
        'last_login': login_history.first(),
        'unique_ips': login_history.values('ip_address').distinct().count(),
    }
    
    # Pagination
    paginator = Paginator(login_history, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'target_user': target_user,
        'login_history': page_obj,
        'stats': stats,
    }
    
    return render(request, 'accounts/user_login_history.html', context)


@login_required
def mark_session_suspicious(request, session_id):
    """Mark a login session as suspicious (Secretary/Chairman only)"""
    if not request.user.can_view_all_login_history():
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    if request.method == 'POST':
        session = get_object_or_404(UserLoginHistory, id=session_id)
        session.is_suspicious = not session.is_suspicious
        session.save()
        
        return JsonResponse({
            'success': True,
            'is_suspicious': session.is_suspicious,
            'message': 'Session marked as suspicious' if session.is_suspicious else 'Session unmarked as suspicious'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def terminate_user_sessions(request, user_id):
    """Terminate all active sessions for a user (Secretary/Chairman only)"""
    if not request.user.can_view_all_login_history():
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')
    
    target_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Mark all active sessions as inactive
        active_sessions = UserLoginHistory.objects.filter(
            user=target_user,
            is_active=True
        )
        
        count = active_sessions.count()
        active_sessions.update(
            is_active=False,
            logout_time=timezone.now()
        )
        
        messages.success(request, f'Terminated {count} active sessions for {target_user.username}.')
        return redirect('accounts:user_login_history', user_id=user_id)
    
    context = {
        'target_user': target_user,
        'active_sessions_count': UserLoginHistory.objects.filter(
            user=target_user,
            is_active=True
        ).count()
    }
    
    return render(request, 'accounts/terminate_sessions_confirm.html', context)
