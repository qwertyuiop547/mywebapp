from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/session/start/', views.start_session, name='start_session'),
    path('api/session/end/', views.end_session, name='end_session'),
    path('api/feedback/', views.submit_feedback, name='submit_feedback'),
    path('api/upload-image/', views.upload_image_api, name='upload_image_api'),
    path('api/alerts/', views.get_alerts_api, name='get_alerts_api'),
    path('admin/knowledge-base/', views.knowledge_base_admin, name='knowledge_base_admin'),
]
