from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from .models import Complaint, ComplaintAttachment, ComplaintComment, ComplaintCategory
from .forms import ComplaintForm, ComplaintUpdateForm, ComplaintCommentForm, ComplaintSearchForm

@login_required
def complaint_list(request):
    form = ComplaintSearchForm(user=request.user, data=request.GET)
    complaints = Complaint.objects.select_related('category', 'complainant', 'assigned_to', 'approved_by')
    
    # Filter based on user role for the base queryset
    if request.user.is_resident():
        # Residents see all their own complaints (approved or not, but NOT rejected)
        base_complaints = complaints.filter(complainant=request.user).exclude(is_approved=False)
    elif request.user.role == 'secretary':
        # Secretary sees all complaints EXCEPT rejected ones (for approval workflow)
        # Once rejected, hindi na dapat makita para di na ma-confuse
        base_complaints = complaints.exclude(is_approved=False)
    elif request.user.role == 'chairman' or request.user.can_manage_complaints():
        # Chairman and other officials only see approved complaints
        base_complaints = complaints.filter(is_approved=True)
    else:
        base_complaints = complaints.exclude(is_approved=False)
    
    # Get statistics for display - calculate from ALL user-accessible complaints (not filtered by search)
    stats = {
        'total': base_complaints.count(),
        'pending': base_complaints.filter(status='pending').count(),
        'in_progress': base_complaints.filter(status='in_progress').count(),
        'resolved': base_complaints.filter(status='resolved').count(),
    }
    
    # Start with base complaints for filtering
    complaints = base_complaints
    
    # Apply search filters only if form is valid
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        status = form.cleaned_data.get('status')
        priority = form.cleaned_data.get('priority')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        assigned_to = form.cleaned_data.get('assigned_to')
        sort_by = form.cleaned_data.get('sort_by')
        
        if search:
            complaints = complaints.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search) |
                Q(complainant__first_name__icontains=search) |
                Q(complainant__last_name__icontains=search) |
                Q(complainant__username__icontains=search) |
                Q(anonymous_contact__icontains=search)  # Allow searching anonymous contact
            )
        
        if category:
            complaints = complaints.filter(category=category)
        
        if status:
            complaints = complaints.filter(status=status)
        
        if priority:
            complaints = complaints.filter(priority=priority)
        
        if date_from:
            complaints = complaints.filter(created_at__date__gte=date_from)
        
        if date_to:
            complaints = complaints.filter(created_at__date__lte=date_to)
        
        if assigned_to:
            complaints = complaints.filter(assigned_to=assigned_to)
        
        # Apply sorting
        if sort_by:
            complaints = complaints.order_by(sort_by)
        else:
            complaints = complaints.order_by('-created_at')
    else:
        # Default sorting when form is not valid
        complaints = complaints.order_by('-created_at')
    
    paginator = Paginator(complaints, 15)  # Increased page size
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'complaints': page_obj,
        'form': form,
        'stats': stats,
        'has_filters': any([
            form.cleaned_data.get('search'),
            form.cleaned_data.get('category'),
            form.cleaned_data.get('status'),
            form.cleaned_data.get('priority'),
            form.cleaned_data.get('date_from'),
            form.cleaned_data.get('date_to'),
            form.cleaned_data.get('assigned_to'),
        ]) if form.is_valid() else False,
    }
    
    return render(request, 'complaints/complaint_list.html', context)

@login_required
def complaint_detail(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    # Check permissions
    if request.user.is_resident() and complaint.complainant != request.user:
        messages.error(request, "You can only view your own complaints.")
        return redirect('complaints:complaint_list')
    
    # Handle comment submission - only for Chairman (NOT Secretary)
    comment_form = None
    # Secretary can only view, NOT add comments or attachments
    # Only Chairman has power to add comments and attach files
    if request.user.can_manage_complaints() and request.user.role != 'secretary':
        if request.method == 'POST':
            comment_form = ComplaintCommentForm(request.user, request.POST, request.FILES)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.complaint = complaint
                comment.author = request.user
                comment.save()
                
                # Show different message if attachment was included
                if comment.attachment:
                    messages.success(request, "Comment with attachment added successfully.")
                else:
                    messages.success(request, "Comment added successfully.")
                return redirect('complaints:complaint_detail', complaint_id=complaint.id)
        else:
            comment_form = ComplaintCommentForm(request.user)
    
    # Get comments (filter internal comments for residents)
    comments = complaint.comments.select_related('author')
    if request.user.is_resident():
        comments = comments.filter(is_internal=False)
    
    context = {
        'complaint': complaint,
        'comments': comments,
        'comment_form': comment_form,
        'attachments': complaint.attachments.all(),
    }
    
    return render(request, 'complaints/complaint_detail.html', context)

def create_complaint(request):
    # Restrict Secretary and Chairman from filing complaints
    if request.user.is_authenticated and request.user.role in ['secretary', 'chairman']:
        messages.error(request, 'Barangay officials cannot file complaints. Officials handle complaints, hindi nag-co-complain.')
        return redirect('complaints:complaint_list')
    
    if request.method == 'POST':
        print(f"POST received: {request.POST}")
        print(f"FILES received: {request.FILES}")
        form = ComplaintForm(request.POST, request.FILES)
        print(f"Form errors: {form.errors}")
        if form.is_valid():
            complaint = form.save(commit=False)
            
            # Handle anonymous vs authenticated complaints
            if form.cleaned_data.get('is_anonymous'):
                complaint.complainant = None  # Anonymous complaint
                complaint.is_anonymous = True
                complaint.anonymous_contact = form.cleaned_data.get('anonymous_contact')
            else:
                # Require authentication for non-anonymous complaints
                if not request.user.is_authenticated:
                    messages.error(request, 'Please log in to submit a non-anonymous complaint.')
                    return redirect('accounts:login')
                complaint.complainant = request.user
                complaint.is_anonymous = False
            
            complaint.save()
            
            # Handle file attachments
            files = request.FILES.getlist('attachments')
            for file in files:
                ComplaintAttachment.objects.create(
                    complaint=complaint,
                    file=file
                )
            
            if complaint.is_anonymous:
                messages.success(request, "Your anonymous complaint has been submitted successfully! Your complaint ID is: " + str(complaint.id))
                return redirect('complaints:anonymous_success', complaint_id=complaint.id)
            else:
                messages.success(request, "Your complaint has been submitted successfully!")
                return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    else:
        form = ComplaintForm()
    
    # Get user's complaint statistics for dashboard welcome section (only if authenticated)
    stats = {'total': 0, 'pending': 0, 'in_progress': 0, 'resolved': 0}
    if request.user.is_authenticated:
        user_complaints = Complaint.objects.filter(complainant=request.user)
        if hasattr(request.user, 'is_resident') and request.user.is_resident():
            # Residents see all their own complaints (approved or not, but NOT rejected)
            user_complaints = user_complaints.exclude(is_approved=False)
        
        stats = {
            'total': user_complaints.count(),
            'pending': user_complaints.filter(status='pending').count(),
            'in_progress': user_complaints.filter(status='in_progress').count(),
            'resolved': user_complaints.filter(status='resolved').count(),
        }
    
    context = {
        'form': form,
        'stats': stats,
        'user': request.user,
    }
    
    return render(request, 'complaints/create_complaint.html', context)

def anonymous_success(request, complaint_id):
    """Success page for anonymous complaints"""
    complaint = get_object_or_404(Complaint, id=complaint_id, is_anonymous=True)
    
    context = {
        'complaint': complaint,
    }
    
    return render(request, 'complaints/anonymous_success.html', context)

@login_required
def update_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    # Check permissions - Secretary CANNOT do Manual Update, only Chairman can
    if not request.user.can_manage_complaints() or request.user.role == 'secretary':
        messages.error(request, "You don't have permission to update complaints. Only Chairman can perform manual updates.")
        return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    
    if request.method == 'POST':
        form = ComplaintUpdateForm(request.POST, request.FILES, instance=complaint, user=request.user)
        if form.is_valid():
            updated_complaint = form.save(commit=False)
            
            # Workflow validation - prevent status skipping
            valid_transitions = {
                'pending': ['in_progress'],
                'in_progress': ['resolved'],
                'resolved': ['closed'],
                'closed': []  # Cannot transition from closed
            }
            
            # Allow status to stay the same or follow valid workflow
            if (updated_complaint.status != complaint.status and 
                updated_complaint.status not in valid_transitions.get(complaint.status, [])):
                    
                messages.error(request, 
                    f"Invalid status transition. {complaint.get_status_display()} can only move to: " +
                    ", ".join([dict(Complaint.STATUS_CHOICES)[s] for s in valid_transitions.get(complaint.status, ['None'])])
                )
                return redirect('complaints:complaint_detail', complaint_id=complaint.id)
            
            # Set resolved timestamp and resolved_by user
            if updated_complaint.status == 'resolved' and not complaint.resolved_at:
                updated_complaint.resolved_at = timezone.now()
                updated_complaint.resolved_by = request.user
            elif updated_complaint.status != 'resolved':
                updated_complaint.resolved_at = None
                updated_complaint.resolved_by = None
            
            updated_complaint.save()
            messages.success(request, "Complaint updated successfully!")
            return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    else:
        form = ComplaintUpdateForm(instance=complaint, user=request.user)
    
    context = {
        'form': form,
        'complaint': complaint,
    }
    
    return render(request, 'complaints/update_complaint.html', context)

@login_required
def delete_attachment(request, attachment_id):
    attachment = get_object_or_404(ComplaintAttachment, id=attachment_id)
    complaint = attachment.complaint
    
    # Check permissions
    if request.user != complaint.complainant and not request.user.can_manage_complaints():
        messages.error(request, "You don't have permission to delete this attachment.")
        return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    
    if request.method == 'POST':
        attachment.delete()
        messages.success(request, "Attachment deleted successfully.")
    
    return redirect('complaints:complaint_detail', complaint_id=complaint.id)

@login_required
def delete_complaint(request, complaint_id):
    """Delete a complaint - only for resolved/closed complaints by admin"""
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    # Check permissions - only admin (secretary/chairman) can delete complaints
    if not request.user.can_manage_complaints():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        messages.error(request, "You don't have permission to delete complaints.")
        return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    
    # Only allow deletion of resolved or closed complaints
    if complaint.status not in ['resolved', 'closed']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Only resolved or closed complaints can be deleted'}, status=400)
        messages.error(request, "Only resolved or closed complaints can be deleted.")
        return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    
    if request.method == 'POST':
        complaint_title = complaint.title
        complaint.delete()
        
        # Handle AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f'Complaint "{complaint_title}" has been permanently deleted.'})
        
        # Regular form submission
        messages.success(request, f'Complaint "{complaint_title}" has been permanently deleted.')
        return redirect('complaints:complaint_list')
    
    # If GET request, show confirmation page
    context = {
        'complaint': complaint,
        'title': 'Delete Complaint'
    }
    return render(request, 'complaints/delete_complaint.html', context)

@login_required
def mark_resolved(request, complaint_id):
    """Mark a complaint as resolved (AJAX endpoint)"""
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    # Check permissions - only Chairman can mark as resolved (NOT Secretary)
    if not request.user.can_manage_complaints() or request.user.role == 'secretary':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Only Chairman can mark complaints as resolved'}, status=403)
        messages.error(request, "Only Chairman can mark complaints as resolved.")
        return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    
    # Don't allow resolving complaints that aren't in progress
    if complaint.status != 'in_progress':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Only complaints in progress can be marked as resolved'}, status=400)
        messages.error(request, "Only complaints in progress can be marked as resolved.")
        return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    
    if request.method == 'POST':
        # Check if this is from the workflow action button (no file upload expected)
        is_workflow_action = not request.FILES.get('resolution_proof')
        
        if is_workflow_action:
            # Workflow action - allow resolving directly (proof can be in comments)
            complaint.status = 'resolved'
            complaint.resolved_at = timezone.now()
            complaint.save()
            
            # Handle AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': f'Complaint "{complaint.title}" has been marked as resolved.',
                    'new_status': 'resolved',
                    'resolved_at': complaint.resolved_at.strftime('%B %d, %Y at %I:%M %p')
                })
            
            messages.success(request, f'Complaint "{complaint.title}" has been marked as resolved.')
            return redirect('complaints:complaint_detail', complaint_id=complaint.id)
        
        else:
            # Modal form submission - require proof upload
            complaint.resolution_proof = request.FILES['resolution_proof']
            complaint.status = 'resolved'
            complaint.resolved_at = timezone.now()
            complaint.save()
            
            # Handle AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': f'Complaint "{complaint.title}" has been marked as resolved with proof.',
                    'new_status': 'resolved',
                    'resolved_at': complaint.resolved_at.strftime('%B %d, %Y at %I:%M %p')
                })
        
        # Regular form submission
        messages.success(request, f'Complaint "{complaint.title}" has been marked as resolved.')
        return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    
    # GET request - not allowed
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@login_required
def accept_complaint(request, complaint_id):
    """Accept a pending complaint (Chairman only - moves to In Progress)"""
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    # Check permissions - only Chairman can accept complaints
    if not request.user.is_chairman():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Only Chairman can accept complaints'}, status=403)
        messages.error(request, "Only Chairman can accept complaints.")
        return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    
    # Only allow accepting pending complaints
    if complaint.status != 'pending':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Only pending complaints can be accepted'}, status=400)
        messages.error(request, "Only pending complaints can be accepted.")
        return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    
    if request.method == 'POST':
        # Accept complaint - move to In Progress
        complaint.status = 'in_progress'
        complaint.assigned_to = request.user  # Assign to Chairman who accepted
        complaint.save()
        
        # Handle AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': f'Complaint "{complaint.title}" has been accepted and is now in progress.',
                'new_status': 'in_progress'
            })
        
        # Regular form submission
        messages.success(request, f'Complaint "{complaint.title}" has been accepted and is now in progress.')
        return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    
    # GET request - not allowed
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@login_required
def close_complaint(request, complaint_id):
    """Close a resolved complaint (Admin only - moves to Closed)"""
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    # Check permissions - only Chairman can close complaints (NOT Secretary)
    if not request.user.can_manage_complaints() or request.user.role == 'secretary':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Only Chairman can close complaints'}, status=403)
        messages.error(request, "Only Chairman can close complaints.")
        return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    
    # Only allow closing resolved complaints
    if complaint.status != 'resolved':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Only resolved complaints can be closed'}, status=400)
        messages.error(request, "Only resolved complaints can be closed.")
        return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    
    if request.method == 'POST':
        # Close complaint
        complaint.status = 'closed'
        complaint.save()
        
        # Handle AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': f'Complaint "{complaint.title}" has been closed.',
                'new_status': 'closed'
            })
        
        # Regular form submission
        messages.success(request, f'Complaint "{complaint.title}" has been closed.')
        return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    
    # GET request - not allowed
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@login_required
def complaint_statistics_api(request):
    """API endpoint for dashboard statistics"""
    if not request.user.can_manage_complaints():
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    stats = {
        'total': Complaint.objects.count(),
        'pending': Complaint.objects.filter(status='pending').count(),
        'in_progress': Complaint.objects.filter(status='in_progress').count(),
        'resolved': Complaint.objects.filter(status='resolved').count(),
        'closed': Complaint.objects.filter(status='closed').count(),
    }
    
    # Category breakdown
    categories = {}
    for category in ComplaintCategory.objects.all():
        categories[category.name] = Complaint.objects.filter(category=category).count()
    
    stats['categories'] = categories
    
    return JsonResponse(stats)

@login_required
def approve_complaint(request, complaint_id):
    """Secretary approves a complaint for chairman review"""
    print(f"DEBUG: approve_complaint called - method: {request.method}, user: {request.user}, role: {getattr(request.user, 'role', 'no role')}")
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    # Check permissions - only secretaries can approve
    if request.user.role != 'secretary':
        print(f"DEBUG: Permission denied - user role is {request.user.role}")
        messages.error(request, "Only secretaries can approve complaints.")
        return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    
    if request.method == 'POST':
        print(f"DEBUG: Processing POST request for complaint {complaint_id}")
        from django.utils import timezone
        from accounts.models import User
        
        # Approve the complaint
        complaint.is_approved = True
        complaint.approved_at = timezone.now()
        complaint.approved_by = request.user
        
        # Auto-assign to Chairman and set to in_progress
        try:
            chairman = User.objects.filter(role='chairman').first()
            if chairman:
                complaint.assigned_to = chairman
                complaint.status = 'in_progress'
                print(f"DEBUG: Auto-assigned complaint to Chairman: {chairman.username}")
        except Exception as e:
            print(f"DEBUG: Error assigning to Chairman: {e}")
        
        complaint.save()
        print(f"DEBUG: Complaint {complaint_id} approved and assigned successfully")
        
        messages.success(request, f"Complaint '{complaint.title}' has been approved and assigned to Chairman for processing.")
        return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    
    print(f"DEBUG: Non-POST request, redirecting back to detail page")
    return redirect('complaints:complaint_detail', complaint_id=complaint.id)

@login_required 
def reject_complaint(request, complaint_id):
    """Secretary rejects a complaint with reason"""
    import logging
    from django.db import transaction
    logger = logging.getLogger(__name__)
    
    logger.info(f"reject_complaint called for complaint_id={complaint_id} by user={request.user.username}")
    
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    # Check permissions - only secretaries can reject
    if request.user.role != 'secretary':
        logger.warning(f"Non-secretary user {request.user.username} attempted to reject complaint {complaint_id}")
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
            return JsonResponse({'success': False, 'error': 'Only secretaries can reject complaints.'}, status=403)
        
        messages.error(request, "Only secretaries can reject complaints.")
        # Clean redirect to detail page without URL parameters
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        return HttpResponseRedirect(reverse('complaints:complaint_detail', args=[complaint.id]))
    
    if request.method == 'POST':
        logger.info(f"Processing POST request for rejection of complaint {complaint_id}")
        rejection_reason = request.POST.get('rejection_reason', '').strip()
        if not rejection_reason:
            logger.warning(f"Empty rejection reason provided for complaint {complaint_id}")
            
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
                return JsonResponse({'success': False, 'error': 'Please provide a reason for rejection.'}, status=400)
            
            messages.error(request, "Please provide a reason for rejection.")
            # Clean redirect to detail page without URL parameters  
            from django.http import HttpResponseRedirect
            from django.urls import reverse
            return HttpResponseRedirect(reverse('complaints:complaint_detail', args=[complaint.id]))
        
        try:
            logger.info(f"About to save rejection for complaint {complaint_id}")
            # Use database transaction to ensure atomicity and prevent hanging
            with transaction.atomic():
                complaint.is_approved = False
                complaint.rejection_reason = rejection_reason
                complaint.approved_by = request.user  # Track who processed it
                complaint.save(update_fields=['is_approved', 'rejection_reason', 'approved_by'])
                
                # Create notification for complainant about rejection
                from notifications.utils import notify_complaint_rejected
                notify_complaint_rejected(complaint)
            
            logger.info(f"Successfully saved rejection for complaint {complaint_id} and created notification")
            
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
                return JsonResponse({'success': True, 'message': f"Complaint '{complaint.title}' has been rejected."})
            
            messages.warning(request, f"Complaint '{complaint.title}' has been rejected and removed from the list.")
            logger.info(f"About to redirect to complaint list after rejection of complaint {complaint_id}")
            # Redirect to complaint list with clean URL (no parameters) to prevent form reopening
            from django.http import HttpResponseRedirect
            from django.urls import reverse
            return HttpResponseRedirect(reverse('complaints:complaint_list'))
            
        except Exception as e:
            logger.error(f"Error during rejection of complaint {complaint_id}: {e}")
            
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
                return JsonResponse({'success': False, 'error': f"An error occurred while rejecting the complaint: {e}"}, status=500)
            
            messages.error(request, f"An error occurred while rejecting the complaint: {e}")
            # Clean redirect to detail page without URL parameters
            from django.http import HttpResponseRedirect
            from django.urls import reverse
            return HttpResponseRedirect(reverse('complaints:complaint_detail', args=[complaint.id]))
    
    logger.info(f"Non-POST request for complaint {complaint_id}, redirecting")
    # Clean redirect to detail page without URL parameters
    from django.http import HttpResponseRedirect
    from django.urls import reverse
    return HttpResponseRedirect(reverse('complaints:complaint_detail', args=[complaint.id]))