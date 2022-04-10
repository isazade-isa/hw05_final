# posts/views.py
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Post, Group, User


def get_page_context(queryset, request):
    paginator = Paginator(queryset, settings.POST_LMT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj,
    }


def index(request):
    post_list = Post.objects.select_related('author', 'group')
    context = get_page_context(post_list, request)
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    context = {
        'group': group,
    }
    context.update(get_page_context(group.posts.select_related('author'),
                                    request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    follow = author.following.exists()
    following = user.is_authenticated and follow
    context = {
        'author': author,
        'following': following,
    }
    context.update(get_page_context(author.posts.select_related('group'),
                                    request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        id=post_id
    )
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if post.author != request.user:
        return redirect('posts:profile', request.user)
    else:
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
        else:
            context = {
                'form': form,
                'is_edit': True,
            }
            return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    user = request.user
    authors = user.follower.values_list('author', flat=True)
    post_list = Post.objects.filter(author__id__in=authors)
    context = get_page_context(post_list, request)
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    user = request.user
    check_follow = Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    if author != user and not check_follow:
        Follow.objects.create(author=author, user=user)
        return redirect('posts:profile', username=username)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def profile_unfollow(request, username):
    user = request.user
    Follow.objects.get(user=user, author__username=username).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
