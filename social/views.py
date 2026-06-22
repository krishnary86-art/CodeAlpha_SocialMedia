from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Exists, OuterRef, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CommentForm, PostForm, ProfileEditForm, RegisterForm
from .models import Comment, Follow, Like, Post


def home(request):
    if request.user.is_authenticated:
        following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
        posts = Post.objects.filter(
            Q(author=request.user) | Q(author_id__in=following_ids)
        ).select_related('author', 'author__profile').annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True),
            is_liked=Exists(Like.objects.filter(post=OuterRef('pk'), user=request.user)),
        )
    else:
        posts = Post.objects.select_related('author', 'author__profile').annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True),
        )[:20]

    return render(request, 'social/home.html', {'posts': posts})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to SnapChat Social! 👻')
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'social/register.html', {'form': form})


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_following = False
    if request.user != profile_user:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    posts = profile_user.posts.select_related('author', 'author__profile').annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True),
        is_liked=Exists(Like.objects.filter(post=OuterRef('pk'), user=request.user)),
    )

    context = {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following,
        'is_own_profile': request.user == profile_user,
    }
    return render(request, 'social/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=request.user.profile)

    return render(request, 'social/edit_profile.html', {'form': form})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Snap posted! 📸')
            return redirect('home')
    else:
        form = PostForm()

    return render(request, 'social/create_post.html', {'form': form})


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'author__profile').annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True),
            is_liked=Exists(Like.objects.filter(post=OuterRef('pk'), user=request.user)),
        ),
        id=post_id,
    )
    comments = post.comments.select_related('author', 'author__profile')
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', post_id=post.id)

    return render(request, 'social/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    })


@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'like_count': post.like_count})

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
@require_POST
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        return redirect('profile', username=username)

    follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)

    if not created:
        follow.delete()
        following = False
    else:
        following = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'following': following,
            'follower_count': target_user.followers.count(),
        })

    return redirect('profile', username=username)


@login_required
def discover(request):
    users = User.objects.exclude(id=request.user.id).annotate(
        follower_count=Count('followers'),
        is_following=Exists(Follow.objects.filter(follower=request.user, following=OuterRef('pk'))),
    ).order_by('-follower_count')[:30]

    return render(request, 'social/discover.html', {'users': users})
