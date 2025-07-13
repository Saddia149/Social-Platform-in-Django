from django.urls import path
from .views import dashboard_view, admin_users_view, admin_posts_view, admin_login_view, admin_logout_view, admin_reports_view, resolve_report_view

urlpatterns = [
    path('', dashboard_view, name='admin-dashboard'),
    path('users/', admin_users_view, name='admin-users'),
    path('posts/', admin_posts_view, name='admin-posts'),
    path('login/', admin_login_view, name='admin-login'),
    path('logout/', admin_logout_view, name='admin-logout'),
    path('reports/', admin_reports_view, name='admin-reports'),
    path('reports/resolve/<int:report_id>/', resolve_report_view, name='resolve-report'),
]
