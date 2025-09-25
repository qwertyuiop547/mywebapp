from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from .models import GalleryPhoto, GalleryCategory, GalleryLike, GalleryComment
from .forms import PhotoUploadForm, PhotoFilterForm, CommentForm

User = get_user_model()


def gallery_list(request):
    """Main gallery page with photo grid"""
    photos = GalleryPhoto.objects.filter(status__in=['approved', 'featured'], is_public=True)
    categories = GalleryCategory.objects.filter(is_active=True).annotate(photo_count=Count('photos'))
    
    # Apply filters
    form = PhotoFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data['category']:
            photos = photos.filter(category=form.cleaned_data['category'])
        if form.cleaned_data['search']:
            search_query = form.cleaned_data['search']
            photos = photos.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(event_name__icontains=search_query) |
                Q(location__icontains=search_query)
            )
        if form.cleaned_data['featured_only']:
            photos = photos.filter(is_featured=True)
    
    # Pagination
    paginator = Paginator(photos, 12)  # 12 photos per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total': photos.count(),
        'featured': photos.filter(is_featured=True).count(),
        'recent': photos.filter(uploaded_at__gte=timezone.now() - timezone.timedelta(days=30)).count(),
        'categories': categories.count(),
    }
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'form': form,
        'stats': stats,
    }
    
    return render(request, 'gallery/gallery_list.html', context)


def photo_detail(request, photo_id):
    """Individual photo detail page"""
    photo = get_object_or_404(GalleryPhoto, id=photo_id, status__in=['approved', 'featured'], is_public=True)
    
    # Increment view count
    photo.increment_views()
    
    # Get related photos
    related_photos = GalleryPhoto.objects.filter(
        category=photo.category,
        status__in=['approved', 'featured'],
        is_public=True
    ).exclude(id=photo.id)[:6]
    
    # Comments
    comments = photo.comments.all()[:10]
    comment_form = CommentForm()
    
    # Check if user liked this photo
    user_liked = False
    if request.user.is_authenticated:
        user_liked = GalleryLike.objects.filter(photo=photo, user=request.user).exists()
    
    context = {
        'photo': photo,
        'related_photos': related_photos,
        'comments': comments,
        'comment_form': comment_form,
        'user_liked': user_liked,
    }
    
    return render(request, 'gallery/photo_detail.html', context)


@login_required
def upload_photo(request):
    """Upload a new photo"""
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.uploaded_by = request.user
            
            # Set default category if not provided
            if not hasattr(photo, 'category') or photo.category is None:
                try:
                    # Try to get a default category or create one
                    default_category = GalleryCategory.objects.filter(is_active=True).first()
                    if not default_category:
                        # Create a default "General" category if none exists
                        default_category = GalleryCategory.objects.create(
                            name="General",
                            slug="general",
                            description="General photos from the community"
                        )
                    photo.category = default_category
                except:
                    # Fallback: create the category if needed
                    photo.category = GalleryCategory.objects.get_or_create(
                        name="General",
                        defaults={
                            'slug': 'general',
                            'description': 'General photos from the community'
                        }
                    )[0]
            
            # Auto-approve all photos - simple memory sharing
            photo.status = 'approved'
            photo.approved_by = request.user
            photo.approved_at = timezone.now()
            
            photo.save()
            
            messages.success(request, 'Memory photo shared successfully!')
            
            return redirect('gallery:photo_detail', photo_id=photo.id)
    else:
        form = PhotoUploadForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'gallery/upload_photo.html', context)


def category_photos(request, category_slug):
    """Photos in a specific category"""
    category = get_object_or_404(GalleryCategory, slug=category_slug, is_active=True)
    photos = GalleryPhoto.objects.filter(
        category=category,
        status__in=['approved', 'featured'],
        is_public=True
    )
    
    # Pagination
    paginator = Paginator(photos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    
    return render(request, 'gallery/category_photos.html', context)


@login_required
def my_photos(request):
    """User's uploaded photos"""
    photos = GalleryPhoto.objects.filter(uploaded_by=request.user)
    
    # Pagination
    paginator = Paginator(photos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total': photos.count(),
        'approved': photos.filter(status='approved').count(),
        'pending': photos.filter(status='pending').count(),
        'featured': photos.filter(is_featured=True).count(),
    }
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
    }
    
    return render(request, 'gallery/my_photos.html', context)


@login_required
def manage_gallery(request):
    """Gallery management for officials"""
    if request.user.role not in ['chairman', 'secretary']:
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    photos = GalleryPhoto.objects.all()
    
    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter:
        photos = photos.filter(status=status_filter)
    
    category_filter = request.GET.get('category')
    if category_filter:
        photos = photos.filter(category_id=category_filter)
    
    # Pagination
    paginator = Paginator(photos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = GalleryCategory.objects.filter(is_active=True)
    
    # Statistics
    stats = {
        'total': GalleryPhoto.objects.count(),
        'pending': GalleryPhoto.objects.filter(status='pending').count(),
        'approved': GalleryPhoto.objects.filter(status='approved').count(),
        'featured': GalleryPhoto.objects.filter(is_featured=True).count(),
    }
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'stats': stats,
        'current_status': status_filter,
        'current_category': category_filter,
    }
    
    return render(request, 'gallery/manage_gallery.html', context)


@login_required
@require_POST
def like_photo(request, photo_id):
    """AJAX endpoint to like/unlike a photo"""
    photo = get_object_or_404(GalleryPhoto, id=photo_id)
    like, created = GalleryLike.objects.get_or_create(photo=photo, user=request.user)
    
    if not created:
        # Unlike
        like.delete()
        liked = False
        photo.likes = max(0, photo.likes - 1)
    else:
        # Like
        liked = True
        photo.likes += 1
    
    photo.save(update_fields=['likes'])
    
    return JsonResponse({
        'liked': liked,
        'total_likes': photo.likes
    })


@login_required
@require_POST
def add_comment(request, photo_id):
    """Add a comment to a photo"""
    photo = get_object_or_404(GalleryPhoto, id=photo_id)
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.photo = photo
        comment.user = request.user
        
        # Mark as official if user is chairman/secretary
        if request.user.role in ['chairman', 'secretary']:
            comment.is_official = True
        
        comment.save()
        messages.success(request, 'Comment added successfully!')
    else:
        messages.error(request, 'Error adding comment. Please try again.')
    
    return redirect('gallery:photo_detail', photo_id=photo.id)


@login_required
@require_POST
def approve_photo(request, photo_id):
    """Approve a photo (Chairman/Secretary only)"""
    if request.user.role not in ['chairman', 'secretary']:
        return HttpResponseForbidden()
    
    photo = get_object_or_404(GalleryPhoto, id=photo_id)
    photo.status = 'approved'
    photo.approved_by = request.user
    photo.approved_at = timezone.now()
    photo.save()
    
    return JsonResponse({'success': True, 'message': 'Photo approved successfully!'})


@login_required
@require_POST
def reject_photo(request, photo_id):
    """Reject a photo (Chairman/Secretary only)"""
    if request.user.role not in ['chairman', 'secretary']:
        return HttpResponseForbidden()
    
    photo = get_object_or_404(GalleryPhoto, id=photo_id)
    photo.status = 'rejected'
    photo.save()
    
    return JsonResponse({'success': True, 'message': 'Photo rejected successfully!'})


@login_required
@require_POST
def feature_photo(request, photo_id):
    """Feature/unfeature a photo (Chairman only)"""
    if request.user.role != 'chairman':
        return HttpResponseForbidden()
    
    photo = get_object_or_404(GalleryPhoto, id=photo_id)
    
    if photo.is_featured:
        photo.is_featured = False
        photo.status = 'approved'
        message = 'Photo unfeatured successfully!'
    else:
        photo.is_featured = True
        photo.status = 'featured'
        message = 'Photo featured successfully!'
    
    photo.save()
    
    return JsonResponse({'success': True, 'message': message, 'is_featured': photo.is_featured})
