from django.urls import path
from . import views

app_name = 'suggestions'

urlpatterns = [
    # Public views
    path('', views.suggestion_list, name='suggestion_list'),
    path('<int:pk>/', views.suggestion_detail, name='suggestion_detail'),
    
    # User actions
    path('submit/', views.submit_suggestion, name='submit_suggestion'),
    path('my-suggestions/', views.my_suggestions, name='my_suggestions'),
    path('<int:pk>/vote/', views.vote_suggestion, name='vote_suggestion'),
    
    # Management (officials only)
    path('manage/', views.manage_suggestions, name='manage_suggestions'),
    path('<int:pk>/review/', views.review_suggestion, name='review_suggestion'),
]

