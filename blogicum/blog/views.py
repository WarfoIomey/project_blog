from django.shortcuts import get_object_or_404
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib.auth import get_user_model

from .models import Post, Category, Comment
from .forms import PostForm, UserForm, CommentForm
from .utils import get_posts
from .mixins import PostEditMixin, CommentEditMixin


POSTS_PER_PAGE = 10

User = get_user_model()


class PostListView(ListView):
    """Получение всех постов"""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        return get_posts()


class CategoryPostView(ListView):
    """Получение постов по категории"""

    model = Post
    paginate_by = POSTS_PER_PAGE
    slug_url_kwarg = 'category_slug'
    template_name = 'blog/category.html'

    def get_queryset(self):
        return get_posts().filter(
            category__slug=self.kwargs['category_slug']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание поста"""

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostDetailView(DetailView):
    """Просмотр поста"""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        post = Post.objects.filter(
            pk=self.kwargs['post_id'],
            is_published=True,
        )
        if not post and not self.request.user.is_anonymous:
            post = Post.objects.filter(
                pk=self.kwargs['post_id'],
                author=self.request.user
            )
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            Comment.objects.select_related('author', 'post')
        )
        return context


class PostUpdateView(PostEditMixin, UpdateView):
    """Изменение поста"""

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(PostEditMixin, DeleteView):
    """Удаление поста"""

    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        context['form'] = PostForm(instance=post)
        return context


class ProfileDetailView(ListView):
    """Обзор профиля"""

    model = Post
    paginate_by = POSTS_PER_PAGE
    template_name = 'blog/profile.html'
    user = None

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.select_related(
            'location', 'author', 'category'
        ).filter(author=self.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
        return context


class ProfileUpdateView(UserPassesTestMixin, UpdateView):
    """Изменение профиля"""

    model = User
    template_name = 'blog/user.html'
    form_class = UserForm

    def test_func(self):
        object = self.get_object()
        return object == self.request.user


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария к посту"""

    post_card = None
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_card = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.post = self.post_card
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.post_card.pk}
        )


class CommentUpdateView(CommentEditMixin, UpdateView):
    """Изменение комментария"""


class CommentDeleteView(CommentEditMixin, DeleteView):
    """Удаление комментария"""
