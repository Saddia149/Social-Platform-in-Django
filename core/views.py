from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.db.models import Q, Count
from .models import CustomUser, Post,Report, Like, Comment, Notification, Message, Tag, Report
from .forms import RegisterForm, PostForm
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

def home_page(request):
    return render(request, 'home.html')

def register_page(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

class MyLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        return reverse_lazy('feed')  # Redirect to feed after login

def logout_user(request):
    logout(request)
    return redirect('home')

@login_required
def profile_page(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    is_following = user.followers.filter(id=request.user.id).exists()
    return render(request, 'profile.html', {
        'user': user,
        'is_following': is_following,
    })

@login_required
def profile_view(request, pk):
    profile_user = get_object_or_404(CustomUser, id=pk)
    posts = Post.objects.filter(user=profile_user).order_by('-created_at')

    is_following = profile_user in request.user.following.all()

    return render(request, 'profile.html', {
        'user': profile_user,  
        'posts': posts,        
        'is_following': is_following,
    })


@login_required
def edit_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            post.content = content
            post.save()
            return redirect('profile', pk=request.user.id)

    return render(request, 'edit_post.html', {'post': post})



@login_required
def delete_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)

    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect('profile', pk=request.user.id)

    return render(request, 'confirm_delete.html', {'post': post})

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        request.user.username = request.POST.get('username', '').strip()
        request.user.email = request.POST.get('email', '').strip()
        request.user.bio = request.POST.get('bio', '').strip()

        # ✅ Handle uploaded profile pic
        if request.FILES.get('profile_pic'):
            request.user.profile_pic = request.FILES['profile_pic']

        request.user.save()
        return redirect('profile', pk=request.user.id)

    return render(request, 'edit_profile.html', {'user': request.user})


def follower_list_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    followers = user.followers.all()
    return render(request, 'followers.html', {'user': user, 'followers': followers})

def following_list_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    following = user.following.all()
    return render(request, 'following.html', {'user': user, 'following': following})


@login_required
def feed_page(request):
 followed_users = request.user.following.all()
 visible_users = list(followed_users) + [request.user]
 posts = Post.objects.filter(user__in=visible_users).order_by('-created_at')
 return render(request, 'feed.html', {'posts': posts})

@login_required
def follow_user_view(request):
    if request.method == 'POST':
        target_id = request.POST.get('target_user_id')
        target_user = get_object_or_404(CustomUser, id=target_id)

        if target_user in request.user.following.all():
            request.user.following.remove(target_user)  # 👋 Unfollow (no notification)
        else:
            request.user.following.add(target_user)     # ✅ Follow

            # 🔔 Create notification if not self-follow
            if target_user != request.user:
                Notification.objects.create(
                    recipient  = target_user,
                    sender     = request.user,
                    notif_type = 'follow'
                )

        return redirect('profile', pk=target_id)


@login_required
def create_post_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

@login_required
def like_post_view(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)

        existing_like = Like.objects.filter(user=request.user, post=post).first()

        if existing_like:
            existing_like.delete()  # 👈 Unlike, no notification
        else:
            Like.objects.create(user=request.user, post=post)

            # 🔔 Notify ONLY if post belongs to someone else
            if post.user != request.user:
                Notification.objects.create(
                    recipient=post.user,
                    sender=request.user,
                    notif_type='like',
                    post=post
                )

    return redirect(request.META.get('HTTP_REFERER', 'explore'))


@login_required
def comment_post_view(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        content  = request.POST.get('content', '').strip()
        post     = get_object_or_404(Post, id=post_id)

        if content:
            comment = Comment.objects.create(
                user=request.user,
                post=post,
                content=content
            )
            if post.user != request.user:
                Notification.objects.create(
                    recipient = post.user,
                    sender    = request.user,
                    notif_type= 'comment',
                    post      = post,
                    message   = content,
                )
        return redirect('post-detail', post_id=post.id)

    # ---------- GET branch ----------
    post_id = request.GET.get('post')
    if post_id:
        return redirect('post-detail', post_id=post_id)
    # fallback if query‑param missing
    return redirect('feed')


def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    user_report = None
    if request.user.is_authenticated:
        user_report = Report.objects.filter(post=post, reporter=request.user).first()

    return render(request, 'post_detail.html', {
        'post': post,
        'user_report': user_report
    })



@login_required
def explore_page(request):
    posts = Post.objects.annotate(num_likes=Count('likes')).order_by('-num_likes')
    paginator = Paginator(posts, 6)  # show 6 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Elided page range for pagination
    page_range = paginator.get_elided_page_range(number=page_obj.number, on_each_side=2, on_ends=1)

    tags = Tag.objects.all()
    return render(request, 'explore.html', {
        'trending_posts': page_obj,
        'page_range': page_range,
        'tags': tags
    })


@login_required
def notifications_page(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')
    unread_notifications = notifications.filter(is_read=False)

    context = {
        'notifications': notifications,
        'unread_notifications': unread_notifications,
    }
    return render(request, 'notifications.html', context)


@login_required
def message_inbox_view(request):
    # Get all users you've messaged or received messages from
    conversations = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('-timestamp')

    # Collect distinct conversation partners
    partner_ids = set()
    for msg in conversations:
        if msg.sender != request.user:
            partner_ids.add(msg.sender.id)
        if msg.recipient != request.user:
            partner_ids.add(msg.recipient.id)

    users = CustomUser.objects.filter(id__in=partner_ids)
    return render(request, 'inbox.html', {'users': users})


@login_required
def send_message_view(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('recipient_id')
        content = request.POST.get('content', '').strip()
        recipient = get_object_or_404(CustomUser, id=receiver_id)

        if content and recipient != request.user:
            Message.objects.create(sender=request.user, recipient=recipient, content=content)

            Notification.objects.create(
                recipient=recipient,
                sender=request.user,
                notif_type='message',
                message=content
            )

        return redirect('message-inbox')


@login_required
def conversation_view(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)

    messages = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).order_by('timestamp')  # oldest first for chat feel

    context = {
        'messages': messages,
        'other_user': other_user,
    }
    return render(request, 'conversation.html', context)


@login_required
def search_view(request):
    query = request.GET.get('q', '').strip()
    posts = Post.objects.filter(content__icontains=query)
    users = CustomUser.objects.filter(username__icontains=query)

    return render(request, 'search_results.html', {
        'query': query,
        'posts': posts,
        'users': users,
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_stats_view(request):
    stats = {
        "users": CustomUser.objects.count(),
        "posts": Post.objects.count(),
        "comments": Comment.objects.count(),
        "messages": Message.objects.count(),
    }
    return render(request, 'admin_stats.html', {'stats': stats})

@user_passes_test(lambda u: u.is_superuser)
def report_list_view(request):
    reports = Report.objects.all()
    return render(request, 'admin_reports.html', {'reports': reports})


@login_required
def submit_report_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    already_reported = Report.objects.filter(reporter=request.user, post=post).exists()

    if not already_reported and request.method == 'POST':
        reason = request.POST.get('reason')
        Report.objects.create(reporter=request.user, post=post, reason=reason)
        messages.success(request, "✅ Report submitted successfully. Our team will review it shortly.")
    elif already_reported:
        messages.warning(request, "⚠️ You've already reported this post.")

    return redirect('post-detail', post_id=post.id)




User = get_user_model()

def user_profile_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    user_posts = user.posts.all().order_by('-created_at')
    return render(request, 'core/user_profile.html', {
        'profile_user': user,
        'user_posts': user_posts
    })


def about_view(request):
    return render(request, 'core/about.html')