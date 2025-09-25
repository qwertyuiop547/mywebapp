from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='list'),
    path('<int:pk>/', views.service_detail, name='service_detail'),
    path('<int:service_id>/request/', views.service_request_create, name='request_create'),
    path('requests/', views.service_request_list, name='request_list'),
    path('requests/<int:pk>/', views.service_request_detail, name='request_detail'),
]