from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

from .models import Suggestion, SuggestionCategory, SuggestionLike, SuggestionComment
from .forms import SuggestionSubmissionForm, SuggestionCommentForm, SuggestionManagementForm, SuggestionFilterForm

User = get_user_model()

def suggestion_list(request):
    """List all public suggestions with filtering and pagination"""
    suggestions = Suggestion.objects.select_related('category', 'submitted_by').prefetch_related('comments')
    
    # Apply filters
    filter_form = SuggestionFilterForm(request.GET)
    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search')
        category = filter_form.cleaned_data.get('category')
        status = filter_form.cleaned_data.get('status')
        priority = filter_form.cleaned_data.get('priority')
        sort_by = filter_form.cleaned_data.get('sort_by') or '-submitted_at'
        
        if search:
            suggestions = suggestions.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        
        if category:
            suggestions = suggestions.filter(category=category)
            
        if status:
            suggestions = suggestions.filter(status=status)
            
        if priority:
            suggestions = suggestions.filter(priority=priority)
            
        suggestions = suggestions.order_by(sort_by)
    else:
        suggestions = suggestions.order_by('-submitted_at')
    
    # Pagination
    paginator = Paginator(suggestions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get statistics
    stats = {
        'total': Suggestion.objects.count(),
        'pending': Suggestion.objects.filter(status='pending').count(),
        'approved': Suggestion.objects.filter(status='approved').count(),
        'implemented': Suggestion.objects.filter(status='implemented').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'stats': stats,
        'categories': SuggestionCategory.objects.filter(is_active=True),
    }
    
    return render(request, 'suggestions/suggestion_list.html', context)

def suggestion_detail(request, suggestion_id):
    """View details of a specific suggestion"""
    suggestion = get_object_or_404(Suggestion, id=suggestion_id)
    
    # Increment view count
    suggestion.increment_views()
    
    # Check if user has liked this suggestion
    user_liked = False
    if request.user.is_authenticated:
        user_liked = SuggestionLike.objects.filter(suggestion=suggestion, user=request.user).exists()
    
    # Handle comment form submission
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = SuggestionCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.suggestion = suggestion
            comment.user = request.user
            # Mark as official if user is chairman or secretary
            comment.is_official = request.user.role in ['chairman', 'secretary']
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('suggestions:suggestion_detail', suggestion_id=suggestion.id)
    else:
        comment_form = SuggestionCommentForm()
    
    context = {
        'suggestion': suggestion,
        'user_liked': user_liked,
        'comment_form': comment_form,
        'comments': suggestion.comments.select_related('user'),
    }
    
    return render(request, 'suggestions/suggestion_detail.html', context)

@login_required
def submit_suggestion(request):
    """Submit a new suggestion"""
    if request.method == 'POST':
        form = SuggestionSubmissionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.submitted_by = request.user
            suggestion.save()
            messages.success(request, 'Your suggestion has been submitted successfully!')
            return redirect('suggestions:suggestion_detail', suggestion_id=suggestion.id)
    else:
        form = SuggestionSubmissionForm()
    
    context = {
        'form': form,
        'categories': SuggestionCategory.objects.filter(is_active=True),
    }
    
    return render(request, 'suggestions/submit_suggestion.html', context)

@login_required
def my_suggestions(request):
    """View user's own suggestions"""
    suggestions = Suggestion.objects.filter(submitted_by=request.user).order_by('-submitted_at')
    
    paginator = Paginator(suggestions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'suggestions/my_suggestions.html', context)

@login_required
@require_POST
def toggle_like(request, suggestion_id):
    """Toggle like status for a suggestion"""
    suggestion = get_object_or_404(Suggestion, id=suggestion_id)
    
    like_obj, created = SuggestionLike.objects.get_or_create(
        suggestion=suggestion,
        user=request.user
    )
    
    if created:
        # Increment likes count
        suggestion.likes += 1
        suggestion.save(update_fields=['likes'])
        liked = True
    else:
        # Remove like and decrement count
        like_obj.delete()
        suggestion.likes = max(0, suggestion.likes - 1)
        suggestion.save(update_fields=['likes'])
        liked = False
    
    return JsonResponse({
        'liked': liked,
        'likes_count': suggestion.likes
    })

@login_required
def manage_suggestions(request):
    """View for barangay officials to manage suggestions"""
    if not hasattr(request.user, 'role') or request.user.role not in ['chairman', 'secretary']:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:resident_dashboard')
    
    suggestions = Suggestion.objects.select_related('category', 'submitted_by').order_by('-submitted_at')
    
    # Apply filters
    filter_form = SuggestionFilterForm(request.GET)
    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search')
        category = filter_form.cleaned_data.get('category')
        status = filter_form.cleaned_data.get('status')
        priority = filter_form.cleaned_data.get('priority')
        sort_by = filter_form.cleaned_data.get('sort_by') or '-submitted_at'
        
        if search:
            suggestions = suggestions.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(submitted_by__username__icontains=search)
            )
        
        if category:
            suggestions = suggestions.filter(category=category)
            
        if status:
            suggestions = suggestions.filter(status=status)
            
        if priority:
            suggestions = suggestions.filter(priority=priority)
            
        suggestions = suggestions.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(suggestions, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get statistics
    stats = {
        'total': Suggestion.objects.count(),
        'pending': Suggestion.objects.filter(status='pending').count(),
        'under_review': Suggestion.objects.filter(status='under_review').count(),
        'approved': Suggestion.objects.filter(status='approved').count(),
        'implemented': Suggestion.objects.filter(status='implemented').count(),
        'rejected': Suggestion.objects.filter(status='rejected').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'stats': stats,
        'can_manage': request.user.role == 'chairman',  # Only chairman can fully manage
    }
    
    return render(request, 'suggestions/manage_suggestions.html', context)

@login_required
def update_suggestion(request, suggestion_id):
    """Update suggestion status and details (for officials)"""
    suggestion = get_object_or_404(Suggestion, id=suggestion_id)
    
    # Only chairman can update suggestions
    if not hasattr(request.user, 'role') or request.user.role != 'chairman':
        messages.error(request, 'You do not have permission to update suggestions.')
        return redirect('suggestions:suggestion_detail', suggestion_id=suggestion.id)
    
    if request.method == 'POST':
        form = SuggestionManagementForm(request.POST, instance=suggestion)
        if form.is_valid():
            suggestion = form.save(commit=False)
            # Mark as reviewed if status changed
            if form.has_changed() and 'status' in form.changed_data:
                suggestion.mark_reviewed(request.user)
            suggestion.save()
            messages.success(request, 'Suggestion updated successfully!')
            return redirect('suggestions:suggestion_detail', suggestion_id=suggestion.id)
    else:
        form = SuggestionManagementForm(instance=suggestion)
    
    context = {
        'suggestion': suggestion,
        'form': form,
    }
    
    return render(request, 'suggestions/update_suggestion.html', context)
