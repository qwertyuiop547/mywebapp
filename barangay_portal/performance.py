"""
Performance Optimization Utilities for Barangay Portal
Provides caching, query optimization, and async processing helpers
"""

from functools import wraps
from django.core.cache import cache
from django.conf import settings
from django.db.models import Prefetch, Q
from django.utils import timezone
from datetime import timedelta
import hashlib
import json


# ============================================================================
# CACHING DECORATORS
# ============================================================================

def cache_view(timeout=300, key_prefix='view'):
    """
    Cache a view's response
    
    Usage:
        @cache_view(timeout=600, key_prefix='dashboard')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Generate cache key from request path and user
            cache_key = generate_cache_key(
                request.path,
                request.user.id if request.user.is_authenticated else None,
                request.GET.dict(),
                prefix=key_prefix
            )
            
            # Try to get from cache
            response = cache.get(cache_key)
            if response is not None:
                return response
            
            # Generate response and cache it
            response = view_func(request, *args, **kwargs)
            cache.set(cache_key, response, timeout)
            return response
        
        return wrapper
    return decorator


def cache_query(timeout=300, key_prefix='query'):
    """
    Cache a query function's result
    
    Usage:
        @cache_query(timeout=600, key_prefix='complaints')
        def get_user_complaints(user_id):
            return Complaint.objects.filter(user_id=user_id)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = generate_cache_key(
                func.__name__,
                args,
                kwargs,
                prefix=key_prefix
            )
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator


def generate_cache_key(*args, prefix='cache'):
    """Generate a unique cache key from arguments"""
    # Convert args to string representation
    key_data = json.dumps(args, sort_keys=True, default=str)
    # Create hash
    key_hash = hashlib.md5(key_data.encode()).hexdigest()
    return f"{prefix}:{key_hash}"


def invalidate_cache(pattern):
    """
    Invalidate cache keys matching a pattern
    
    Usage:
        invalidate_cache('complaints:*')
    """
    try:
        # This requires django-redis or similar cache backend
        from django.core.cache import cache as default_cache
        if hasattr(default_cache, 'delete_pattern'):
            default_cache.delete_pattern(pattern)
    except:
        pass


# ============================================================================
# QUERY OPTIMIZATION HELPERS
# ============================================================================

class OptimizedQueryMixin:
    """
    Mixin to add query optimization methods to views
    
    Usage:
        class MyView(OptimizedQueryMixin, View):
            def get_queryset(self):
                return self.optimize_queryset(
                    MyModel.objects.all(),
                    select=['user', 'category'],
                    prefetch=['comments', 'attachments']
                )
    """
    
    @staticmethod
    def optimize_queryset(queryset, select=None, prefetch=None, only=None, defer=None):
        """
        Apply query optimizations to a queryset
        
        Args:
            queryset: Base queryset
            select: List of relations to select_related
            prefetch: List of relations to prefetch_related
            only: List of fields to only() fetch
            defer: List of fields to defer() fetching
        """
        if select:
            queryset = queryset.select_related(*select)
        
        if prefetch:
            queryset = queryset.prefetch_related(*prefetch)
        
        if only:
            queryset = queryset.only(*only)
        
        if defer:
            queryset = queryset.defer(*defer)
        
        return queryset
    
    @staticmethod
    def add_pagination(queryset, page_number, per_page=20):
        """
        Add pagination to queryset with optimization
        
        Returns: (page_obj, has_previous, has_next)
        """
        from django.core.paginator import Paginator
        
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page_number)
        
        return page_obj, page_obj.has_previous(), page_obj.has_next()


def optimize_complaints_query(user, base_queryset=None):
    """
    Optimized query for complaints with proper relations
    Returns a queryset with all necessary relations preloaded
    """
    from complaints.models import Complaint, ComplaintComment
    
    if base_queryset is None:
        qs = Complaint.objects.all()
    else:
        qs = base_queryset
    
    # Select related for single foreign keys
    qs = qs.select_related(
        'category',
        'complainant',
        'assigned_to',
        'approved_by'
    )
    
    # Prefetch related for reverse relations
    qs = qs.prefetch_related(
        'attachments',
        Prefetch('comments', queryset=ComplaintComment.objects.select_related('user'))
    )
    
    # Defer heavy text fields if not needed immediately
    # qs = qs.defer('description')  # Uncomment if description not needed in list view
    
    return qs


def optimize_suggestions_query(base_queryset=None):
    """Optimized query for suggestions"""
    from suggestions.models import Suggestion
    
    if base_queryset is None:
        qs = Suggestion.objects.all()
    else:
        qs = base_queryset
    
    return qs.select_related('submitted_by').prefetch_related('votes')


def optimize_gallery_query(base_queryset=None):
    """Optimized query for gallery photos"""
    from gallery.models import GalleryPhoto
    
    if base_queryset is None:
        qs = GalleryPhoto.objects.all()
    else:
        qs = base_queryset
    
    return qs.select_related('category', 'uploaded_by').prefetch_related('likes', 'comments')


# ============================================================================
# STATISTICS CACHING
# ============================================================================

@cache_query(timeout=600, key_prefix='stats')
def get_dashboard_stats(user_id=None, user_role=None):
    """
    Get cached dashboard statistics
    
    Cache for 10 minutes to reduce database load
    """
    from complaints.models import Complaint
    from feedback.models import Feedback
    from accounts.models import User
    from suggestions.models import Suggestion
    
    stats = {
        'total_complaints': Complaint.objects.count(),
        'pending_complaints': Complaint.objects.filter(status='pending').count(),
        'in_progress_complaints': Complaint.objects.filter(status='in_progress').count(),
        'resolved_complaints': Complaint.objects.filter(status='resolved').count(),
        'total_feedback': Feedback.objects.count(),
        'total_suggestions': Suggestion.objects.count(),
        'total_residents': User.objects.filter(role='resident', is_approved=True).count(),
        'pending_approvals': User.objects.filter(role='resident', is_approved=False).count(),
    }
    
    # User-specific stats
    if user_id and user_role == 'resident':
        stats.update({
            'my_complaints': Complaint.objects.filter(complainant_id=user_id).count(),
            'my_resolved': Complaint.objects.filter(complainant_id=user_id, status='resolved').count(),
        })
    
    return stats


@cache_query(timeout=1800, key_prefix='analytics')
def get_analytics_data(days=30):
    """
    Get cached analytics data for charts
    
    Cache for 30 minutes
    """
    from complaints.models import Complaint, ComplaintCategory
    from django.db.models import Count
    from django.db.models.functions import TruncDate
    
    start_date = timezone.now().date() - timedelta(days=days)
    
    # Category distribution
    category_stats = list(
        ComplaintCategory.objects.annotate(
            count=Count('complaint')
        ).values('name', 'count').order_by('-count')
    )
    
    # Daily trends
    daily_trends = list(
        Complaint.objects.filter(created_at__date__gte=start_date)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    
    # Status distribution
    status_stats = dict(
        Complaint.objects.values('status')
        .annotate(count=Count('id'))
        .values_list('status', 'count')
    )
    
    return {
        'categories': category_stats,
        'daily_trends': daily_trends,
        'status_distribution': status_stats,
    }


# ============================================================================
# ASYNC PROCESSING HELPERS
# ============================================================================

def process_async(task_func):
    """
    Decorator to process function asynchronously using Django's async support
    
    Usage:
        @process_async
        def send_notification(user_id, message):
            # Heavy processing here
            pass
    """
    @wraps(task_func)
    def wrapper(*args, **kwargs):
        try:
            # Try to use Celery if available
            from celery import current_app
            return current_app.send_task(task_func.__name__, args=args, kwargs=kwargs)
        except ImportError:
            # Fallback to threading for simple async
            import threading
            thread = threading.Thread(target=task_func, args=args, kwargs=kwargs)
            thread.daemon = True
            thread.start()
            return thread
    
    return wrapper


# ============================================================================
# IMAGE OPTIMIZATION
# ============================================================================

def optimize_image(image_path, max_width=1920, max_height=1080, quality=85):
    """
    Optimize an uploaded image
    
    Args:
        image_path: Path to image file
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        quality: JPEG quality (1-100)
    
    Returns: Optimized image path
    """
    from PIL import Image
    import os
    
    try:
        # Open image
        img = Image.open(image_path)
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Resize if needed
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save optimized
        img.save(image_path, 'JPEG', quality=quality, optimize=True)
        
        return image_path
    except Exception as e:
        # Log error but don't fail
        print(f"Image optimization error: {e}")
        return image_path


def create_thumbnail(image_path, size=(300, 300)):
    """
    Create a thumbnail for an image
    
    Returns: Thumbnail path
    """
    from PIL import Image
    import os
    
    try:
        # Generate thumbnail filename
        base, ext = os.path.splitext(image_path)
        thumb_path = f"{base}_thumb{ext}"
        
        # Create thumbnail
        img = Image.open(image_path)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        img.save(thumb_path, 'JPEG', quality=85, optimize=True)
        
        return thumb_path
    except Exception as e:
        print(f"Thumbnail creation error: {e}")
        return image_path


# ============================================================================
# BULK OPERATIONS
# ============================================================================

def bulk_update_optimized(model, objects, fields, batch_size=100):
    """
    Optimized bulk update using Django's bulk_update
    
    Usage:
        complaints = Complaint.objects.all()
        for complaint in complaints:
            complaint.status = 'updated'
        
        bulk_update_optimized(Complaint, complaints, ['status'])
    """
    from django.db import models
    
    # Convert to list if queryset
    if isinstance(objects, models.QuerySet):
        objects = list(objects)
    
    # Bulk update in batches
    for i in range(0, len(objects), batch_size):
        batch = objects[i:i + batch_size]
        model.objects.bulk_update(batch, fields, batch_size=batch_size)


# ============================================================================
# LAZY LOADING HELPERS
# ============================================================================

def lazy_load_data(request):
    """
    Check if request is for lazy loading (AJAX)
    
    Returns: Boolean
    """
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def paginate_for_ajax(queryset, page, per_page=20):
    """
    Paginate data for AJAX requests
    
    Returns: dict with pagination data
    """
    from django.core.paginator import Paginator
    
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page)
    
    return {
        'items': list(page_obj),
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_count': paginator.count,
    }


# ============================================================================
# RESPONSE TIME MONITORING
# ============================================================================

class ResponseTimeMiddleware:
    """
    Middleware to monitor response times
    
    Add to MIDDLEWARE in settings.py:
        'barangay_portal.performance.ResponseTimeMiddleware'
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        import time
        
        # Start timer
        start_time = time.time()
        
        # Process request
        response = self.get_response(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Add header
        response['X-Response-Time'] = f"{duration:.3f}s"
        
        # Log slow requests (> 1 second)
        if duration > 1.0:
            print(f"SLOW REQUEST: {request.path} took {duration:.3f}s")
        
        return response


# ============================================================================
# DATABASE CONNECTION POOLING
# ============================================================================

def optimize_db_settings():
    """
    Get optimized database settings for better performance
    
    Add to settings.py DATABASES configuration:
        DATABASES = {
            'default': {
                ...
                'OPTIONS': optimize_db_settings(),
            }
        }
    """
    return {
        'connect_timeout': 10,
        'options': '-c statement_timeout=30000',  # 30 seconds
    }


# ============================================================================
# EXPORT UTILITIES
# ============================================================================

__all__ = [
    'cache_view',
    'cache_query',
    'generate_cache_key',
    'invalidate_cache',
    'OptimizedQueryMixin',
    'optimize_complaints_query',
    'optimize_suggestions_query',
    'optimize_gallery_query',
    'get_dashboard_stats',
    'get_analytics_data',
    'process_async',
    'optimize_image',
    'create_thumbnail',
    'bulk_update_optimized',
    'lazy_load_data',
    'paginate_for_ajax',
    'ResponseTimeMiddleware',
]

