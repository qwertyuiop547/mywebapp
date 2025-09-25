from django.urls import path
from . import views

app_name = 'suggestions'

urlpatterns = [
    # Public views
    path('', views.suggestion_list, name='suggestion_list'),
    path('<int:suggestion_id>/', views.suggestion_detail, name='suggestion_detail'),
    
    # User actions
    path('submit/', views.submit_suggestion, name='submit_suggestion'),
    path('my-suggestions/', views.my_suggestions, name='my_suggestions'),
    path('<int:suggestion_id>/like/', views.toggle_like, name='toggle_like'),
    
    # Management views (for officials)
    path('manage/', views.manage_suggestions, name='manage_suggestions'),
    path('<int:suggestion_id>/update/', views.update_suggestion, name='update_suggestion'),
]
