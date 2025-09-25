from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('resident/', views.resident_dashboard, name='resident_dashboard'),
    path('secretary/', views.secretary_dashboard, name='secretary_dashboard'),
    path('chairman/', views.chairman_dashboard, name='chairman_dashboard'),
    path('reports/', views.reports_view, name='reports'),
]