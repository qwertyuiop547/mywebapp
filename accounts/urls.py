from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('wait-approval/', views.wait_approval_view, name='wait_approval'),
    path('user-approval/', views.user_approval_list, name='user_approval'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject-user/<int:user_id>/', views.reject_user, name='reject_user'),
    path('view-documents/<int:user_id>/', views.view_user_documents, name='view_documents'),
    path('view-document/<int:user_id>/<int:document_id>/', views.view_single_document, name='view_single_document'),
    path('view-profile/<int:user_id>/', views.view_user_profile, name='view_user_profile'),
    path('delete-account/confirm/', views.delete_account_confirm, name='delete_account_confirm'),
    path('delete-account/execute/', views.delete_own_account, name='delete_own_account'),
    
    # Chairman User Management
    path('user-management/', views.user_management_list, name='user_management'),
    path('deactivate-user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('activate-user/<int:user_id>/', views.activate_user, name='activate_user'),
    path('delete-user/<int:user_id>/', views.delete_user_account, name='delete_user_account'),
    
    # Residents Map
    path('residents-map/', views.residents_map_view, name='residents_map'),
    
    # Automatic Residency Validation
    path('validate-residency/', views.validate_residency, name='validate_residency'),
    path('validation-status/', views.get_validation_status, name='validation_status'),
    
    # Login History & Device Management
    path('login-history/', views.login_history_view, name='login_history'),
    path('user-login-history/<int:user_id>/', views.user_login_history_view, name='user_login_history'),
    path('mark-session-suspicious/<int:session_id>/', views.mark_session_suspicious, name='mark_session_suspicious'),
    path('terminate-sessions/<int:user_id>/', views.terminate_user_sessions, name='terminate_user_sessions'),
]