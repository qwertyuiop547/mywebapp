from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import ServiceCategory, Service, ServiceRequest

def service_list(request):
    """Display all available barangay services"""
    categories = ServiceCategory.objects.filter(is_active=True).prefetch_related('services')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        services = Service.objects.filter(
            Q(name__icontains=search_query) |
            Q(name_filipino__icontains=search_query) |
            Q(description__icontains=search_query),
            is_active=True
        ).select_related('category')
    else:
        services = None
    
    context = {
        'categories': categories,
        'services': services,
        'search_query': search_query,
    }
    return render(request, 'services/service_list.html', context)

def service_detail(request, pk):
    """Display detailed information about a specific service"""
    service = get_object_or_404(Service, pk=pk, is_active=True)
    
    context = {
        'service': service,
    }
    return render(request, 'services/service_detail.html', context)

@login_required
def service_request_create(request, service_id):
    """Create a new service request"""
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    
    if not service.is_online_available:
        messages.error(request, 'This service is not available for online requests. Please visit the barangay office.')
        return redirect('services:service_detail', pk=service.pk)
    
    if request.method == 'POST':
        # Handle form submission
        service_request = ServiceRequest.objects.create(
            service=service,
            requester=request.user,
            full_name=request.POST.get('full_name'),
            contact_number=request.POST.get('contact_number'),
            email=request.POST.get('email', ''),
            address=request.POST.get('address'),
            purpose=request.POST.get('purpose'),
            purpose_filipino=request.POST.get('purpose_filipino', ''),
            priority=request.POST.get('priority', 'normal'),
        )
        
        messages.success(request, f'Your service request has been submitted successfully! Reference Number: {service_request.reference_number}')
        return redirect('services:request_detail', pk=service_request.pk)
    
    context = {
        'service': service,
    }
    return render(request, 'services/service_request_form.html', context)

@login_required
def service_request_list(request):
    """Display user's service requests"""
    requests = ServiceRequest.objects.filter(requester=request.user).select_related('service')
    
    context = {
        'requests': requests,
    }
    return render(request, 'services/service_request_list.html', context)

@login_required
def service_request_detail(request, pk):
    """Display detailed information about a service request"""
    service_request = get_object_or_404(ServiceRequest, pk=pk)
    
    # Check if user owns this request or is staff
    if service_request.requester != request.user and not request.user.can_manage_complaints():
        messages.error(request, 'You do not have permission to view this request.')
        return redirect('services:request_list')
    
    context = {
        'service_request': service_request,
    }
    return render(request, 'services/service_request_detail.html', context)
