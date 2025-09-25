from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('preferences/', views.notification_preferences, name='preferences'),
    path('view/<int:notification_id>/', views.notification_detail, name='notification_detail'),
    path('mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark_all_read'),
    path('delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('delete-all/', views.delete_all_notifications, name='delete_all_notifications'),
    
    # API endpoints
    path('api/list/', views.get_recent_notifications, name='api_list'),
    path('api/unread-count/', views.get_unread_notifications_count, name='api_unread_count'),
    path('api/recent/', views.get_recent_notifications, name='api_recent'),
]