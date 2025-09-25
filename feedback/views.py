from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.http import JsonResponse
from .models import Feedback, FeedbackAttachment
from .forms import FeedbackForm, FeedbackResponseForm, FeedbackFilterForm

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            
            # Handle attachment
            if form.cleaned_data.get('attachment'):
                FeedbackAttachment.objects.create(
                    feedback=feedback,
                    file=form.cleaned_data['attachment']
                )
            
            messages.success(request, "Thank you for your feedback! It has been submitted successfully.")
            return redirect('feedback:feedback_list')
    else:
        form = FeedbackForm()
    
    return render(request, 'feedback/submit_feedback.html', {'form': form})

@login_required
def feedback_list(request):
    form = FeedbackFilterForm(request.GET)
    feedbacks = Feedback.objects.select_related('user', 'reviewed_by')
    
    # Filter based on user role
    if request.user.is_resident():
        feedbacks = feedbacks.filter(user=request.user)
    
    # Apply filters
    if form.is_valid():
        feedback_type = form.cleaned_data.get('feedback_type')
        rating = form.cleaned_data.get('rating')
        reviewed = form.cleaned_data.get('reviewed')
        search = form.cleaned_data.get('search')
        
        if feedback_type:
            feedbacks = feedbacks.filter(feedback_type=feedback_type)
        
        if rating:
            feedbacks = feedbacks.filter(rating=rating)
        
        if reviewed == 'yes':
            feedbacks = feedbacks.filter(is_reviewed=True)
        elif reviewed == 'no':
            feedbacks = feedbacks.filter(is_reviewed=False)
        
        if search:
            feedbacks = feedbacks.filter(
                Q(title__icontains=search) |
                Q(comment__icontains=search)
            )
    
    paginator = Paginator(feedbacks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics for the dashboard
    all_feedbacks = Feedback.objects.all()
    stats = {
        'total_feedback': all_feedbacks.count(),
        'excellent_feedback': all_feedbacks.filter(rating=5).count(),
        'good_feedback': all_feedbacks.filter(rating=4).count(),
        'needs_response': all_feedbacks.filter(is_reviewed=False).count(),
    }
    
    context = {
        'feedbacks': page_obj,
        'form': form,
        'total_feedbacks': feedbacks.count(),
        'stats': stats,
    }
    
    return render(request, 'feedback/feedback_list.html', context)

@login_required
def feedback_detail(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    
    # Check permissions
    if request.user.is_resident() and feedback.user != request.user:
        messages.error(request, "You can only view your own feedback.")
        return redirect('feedback:feedback_list')
    
    # Handle admin response
    if request.method == 'POST' and request.user.can_manage_complaints():
        response_form = FeedbackResponseForm(request.POST, instance=feedback)
        if response_form.is_valid():
            feedback = response_form.save(commit=False)
            feedback.is_reviewed = True
            feedback.reviewed_by = request.user
            feedback.reviewed_at = timezone.now()
            feedback.save()
            messages.success(request, "Response added successfully.")
            return redirect('feedback:feedback_detail', feedback_id=feedback.id)
    else:
        response_form = FeedbackResponseForm(instance=feedback)
    
    context = {
        'feedback': feedback,
        'response_form': response_form,
        'attachments': feedback.attachments.all(),
    }
    
    return render(request, 'feedback/feedback_detail.html', context)

@login_required
def feedback_statistics(request):
    if not request.user.can_manage_complaints():
        messages.error(request, "You don't have permission to view statistics.")
        return redirect('feedback:feedback_list')
    
    # Overall statistics
    total_feedback = Feedback.objects.count()
    avg_rating = Feedback.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    # Rating distribution
    rating_stats = {}
    for i in range(1, 6):
        rating_stats[f'{i}_star'] = Feedback.objects.filter(rating=i).count()
    
    # Feedback type distribution
    type_stats = {}
    for choice in Feedback.FEEDBACK_TYPE_CHOICES:
        type_stats[choice[1]] = Feedback.objects.filter(feedback_type=choice[0]).count()
    
    # Recent feedback
    recent_feedback = Feedback.objects.select_related('user')[:5]
    
    context = {
        'total_feedback': total_feedback,
        'avg_rating': round(avg_rating, 1),
        'rating_stats': rating_stats,
        'type_stats': type_stats,
        'recent_feedback': recent_feedback,
    }
    
    return render(request, 'feedback/feedback_statistics.html', context)

@login_required
def feedback_statistics_api(request):
    """API endpoint for dashboard statistics"""
    if not request.user.can_manage_complaints():
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    stats = {
        'total': Feedback.objects.count(),
        'avg_rating': Feedback.objects.aggregate(avg=Avg('rating'))['avg'] or 0,
        'by_rating': {},
        'by_type': {},
        'reviewed': Feedback.objects.filter(is_reviewed=True).count(),
        'unreviewed': Feedback.objects.filter(is_reviewed=False).count(),
    }
    
    # Rating breakdown
    for i in range(1, 6):
        stats['by_rating'][f'{i}_stars'] = Feedback.objects.filter(rating=i).count()
    
    # Type breakdown
    for choice in Feedback.FEEDBACK_TYPE_CHOICES:
        stats['by_type'][choice[1]] = Feedback.objects.filter(feedback_type=choice[0]).count()
    
    return JsonResponse(stats)