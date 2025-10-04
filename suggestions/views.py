from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Suggestion, SuggestionVote
from .forms import SuggestionForm, SuggestionReviewForm, SuggestionFilterForm


def suggestion_list(request):
    """
    Display all suggestions with filtering
    """
    suggestions = Suggestion.objects.select_related('submitted_by').all()
    
    # Apply filters
    filter_form = SuggestionFilterForm(request.GET)
    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search')
        status = filter_form.cleaned_data.get('status')
        
        if search:
            suggestions = suggestions.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        
        if status:
            suggestions = suggestions.filter(status=status)
    
    # Pagination
    paginator = Paginator(suggestions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Stats
    stats = {
        'total': Suggestion.objects.count(),
        'pending': Suggestion.objects.filter(status='pending').count(),
        'approved': Suggestion.objects.filter(status='approved').count(),
        'completed': Suggestion.objects.filter(status='completed').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'stats': stats,
    }
    
    return render(request, 'suggestions/suggestion_list.html', context)


def suggestion_detail(request, pk):
    """
    View a single suggestion in detail
    """
    suggestion = get_object_or_404(Suggestion, pk=pk)
    
    # Check if current user voted
    user_voted = False
    if request.user.is_authenticated:
        user_voted = SuggestionVote.objects.filter(
            suggestion=suggestion,
            user=request.user
        ).exists()
    
    context = {
        'suggestion': suggestion,
        'user_voted': user_voted,
    }
    
    return render(request, 'suggestions/suggestion_detail.html', context)


@login_required
def submit_suggestion(request):
    """
    Submit a new suggestion
    """
    if request.method == 'POST':
        form = SuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.submitted_by = request.user
            suggestion.save()
            messages.success(request, 'Salamat! Naipadala na ang iyong mungkahi.')
            return redirect('suggestions:suggestion_detail', pk=suggestion.pk)
    else:
        form = SuggestionForm()
    
    return render(request, 'suggestions/submit_suggestion.html', {'form': form})


@login_required
def my_suggestions(request):
    """
    View user's own suggestions
    """
    suggestions = Suggestion.objects.filter(submitted_by=request.user).order_by('-submitted_at')
    
    paginator = Paginator(suggestions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'suggestions/my_suggestions.html', {'page_obj': page_obj})


@login_required
@require_POST
def vote_suggestion(request, pk):
    """
    Vote for a suggestion (AJAX)
    """
    suggestion = get_object_or_404(Suggestion, pk=pk)
    
    vote, created = SuggestionVote.objects.get_or_create(
        suggestion=suggestion,
        user=request.user
    )
    
    if created:
        # New vote
        suggestion.upvotes += 1
        suggestion.save()
        voted = True
    else:
        # Remove vote
        vote.delete()
        suggestion.upvotes = max(0, suggestion.upvotes - 1)
        suggestion.save()
        voted = False
    
    return JsonResponse({
        'success': True,
        'voted': voted,
        'upvotes': suggestion.upvotes
    })


@login_required
def manage_suggestions(request):
    """
    Manage suggestions (for barangay officials only)
    """
    # Check if user is official
    if not hasattr(request.user, 'role') or request.user.role not in ['chairman', 'secretary', 'official']:
        messages.error(request, 'Walang access. Officials lang po.')
        return redirect('suggestions:suggestion_list')
    
    suggestions = Suggestion.objects.select_related('submitted_by').order_by('-submitted_at')
    
    # Apply filters
    filter_form = SuggestionFilterForm(request.GET)
    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search')
        status = filter_form.cleaned_data.get('status')
        
        if search:
            suggestions = suggestions.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        if status:
            suggestions = suggestions.filter(status=status)
    
    # Pagination
    paginator = Paginator(suggestions, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Stats
    stats = {
        'total': Suggestion.objects.count(),
        'pending': Suggestion.objects.filter(status='pending').count(),
        'reviewing': Suggestion.objects.filter(status='reviewing').count(),
        'approved': Suggestion.objects.filter(status='approved').count(),
        'completed': Suggestion.objects.filter(status='completed').count(),
        'rejected': Suggestion.objects.filter(status='rejected').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'stats': stats,
    }
    
    return render(request, 'suggestions/manage_suggestions.html', context)


@login_required
def review_suggestion(request, pk):
    """
    Review a suggestion (for officials)
    """
    # Check if user is official
    if not hasattr(request.user, 'role') or request.user.role not in ['chairman', 'secretary', 'official']:
        messages.error(request, 'Walang access. Officials lang po.')
        return redirect('suggestions:suggestion_detail', pk=pk)
    
    suggestion = get_object_or_404(Suggestion, pk=pk)
    
    if request.method == 'POST':
        form = SuggestionReviewForm(request.POST, instance=suggestion)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.mark_as_reviewed(request.user)
            suggestion.save()
            messages.success(request, 'Na-update na ang suggestion.')
            return redirect('suggestions:suggestion_detail', pk=suggestion.pk)
    else:
        form = SuggestionReviewForm(instance=suggestion)
    
    context = {
        'suggestion': suggestion,
        'form': form,
    }
    
    return render(request, 'suggestions/review_suggestion.html', context)
