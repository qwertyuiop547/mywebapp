from django.urls import path
from . import views

app_name = 'complaints'

urlpatterns = [
    path('', views.complaint_list, name='complaint_list'),
    path('create/', views.create_complaint, name='create_complaint'),
    path('<int:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    path('anonymous-success/<int:complaint_id>/', views.anonymous_success, name='anonymous_success'),
    path('<int:complaint_id>/update/', views.update_complaint, name='update_complaint'),
    path('<int:complaint_id>/approve/', views.approve_complaint, name='approve_complaint'),
    path('<int:complaint_id>/reject/', views.reject_complaint, name='reject_complaint'),
    path('<int:complaint_id>/accept/', views.accept_complaint, name='accept_complaint'),
    path('<int:complaint_id>/mark-resolved/', views.mark_resolved, name='mark_resolved'),
    path('<int:complaint_id>/close/', views.close_complaint, name='close_complaint'),
    path('<int:complaint_id>/delete/', views.delete_complaint, name='delete_complaint'),
    path('attachment/<int:attachment_id>/delete/', views.delete_attachment, name='delete_attachment'),
    path('api/statistics/', views.complaint_statistics_api, name='statistics_api'),
]