from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    # Main gallery pages
    path('', views.gallery_list, name='gallery_list'),
    path('photo/<int:photo_id>/', views.photo_detail, name='photo_detail'),
    path('category/<slug:category_slug>/', views.category_photos, name='category_photos'),
    
    # Photo management
    path('upload/', views.upload_photo, name='upload_photo'),
    path('my-photos/', views.my_photos, name='my_photos'),
    path('manage/', views.manage_gallery, name='manage_gallery'),
    
    # AJAX endpoints
    path('photo/<int:photo_id>/like/', views.like_photo, name='like_photo'),
    path('photo/<int:photo_id>/comment/', views.add_comment, name='add_comment'),
    
    # Management actions (officials only)
    path('photo/<int:photo_id>/approve/', views.approve_photo, name='approve_photo'),
    path('photo/<int:photo_id>/reject/', views.reject_photo, name='reject_photo'),
    path('photo/<int:photo_id>/feature/', views.feature_photo, name='feature_photo'),
]
