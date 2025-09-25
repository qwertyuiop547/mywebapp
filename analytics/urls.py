from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_overview, name='overview'),
    path('complaints/', views.analytics_complaints, name='complaints'),
    path('feedback/', views.analytics_feedback, name='feedback'),
    path('export/', views.analytics_export, name='export'),
]