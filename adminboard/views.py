from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from core.models import CustomUser, Post, Message, Notification, Report
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.contrib.auth import get_user_model


def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def dashboard_view(request):
    total_users = CustomUser.objects.filter(is_superuser=False, is_staff=False).count()
    total_posts = Post.objects.count()
    total_messages = Message.objects.count()
    total_notifications = Notification.objects.count()

    return render(request, 'adminboard/dashboard.html', {
        'total_users': total_users,
        'total_posts': total_posts,
        'total_messages': total_messages,
        'total_notifications': total_notifications,
    })


@login_required
@user_passes_test(is_admin)
def admin_users_view(request):
    users = CustomUser.objects.filter(is_superuser=False, is_staff=False).order_by('-date_joined')
    return render(request, 'adminboard/users.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def admin_posts_view(request):
    posts = Post.objects.select_related('user').order_by('-created_at')
    return render(request, 'adminboard/posts.html', {'posts': posts})

def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            try:
                user = get_user_model().objects.get(username=username)
                if user.check_password(password):
                    if user.is_active and (user.is_staff or user.is_superuser):
                        login(request, user)
                        return redirect('admin-dashboard')
                    messages.error(request, "Account not active or lacks privileges")
                else:
                    messages.error(request, "Invalid password")
            except get_user_model().DoesNotExist:
                messages.error(request, "Username not found")
        else:
            if user.is_active and (user.is_staff or user.is_superuser):
                login(request, user)
                return redirect('admin-dashboard')
            messages.error(request, "Account not active or lacks privileges")
    
    return render(request, 'adminboard/admin_login.html')


@never_cache
def admin_logout_view(request):
    if request.user.is_authenticated:
        request.session.flush()
        logout(request)
        request.session.create()
    return redirect('admin-login')


@login_required
@user_passes_test(is_admin)
def admin_reports_view(request):
    from core.models import Report  # or wherever your Report model lives
    reports = Report.objects.select_related('post', 'reporter').order_by('-timestamp')
    
    return render(request, 'adminboard/reports.html', {'reports': reports})


@login_required
@user_passes_test(lambda u: u.is_staff)
def resolve_report_view(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    report.is_resolved = True
    report.save()
    messages.success(request, f"✅ Report #{report.id} has been marked as resolved.")
    return redirect('admin-reports')