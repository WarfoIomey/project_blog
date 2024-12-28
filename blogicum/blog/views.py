from django.shortcuts import get_object_or_404, render
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.list import MultipleObjectMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse

from datetime import datetime

from .models import Post, Category, Comment
from .forms import PostForm, UserForm, CommentForm


POSTS_PER_PAGE = 5


def get_posts():
    """Получение постов"""
    now = datetime.today()
    return Post.objects.select_related(
        'location', 'author', 'category'
    ).filter(
        is_published=True,
        pub_date__lt=now,
        category__is_published=True
    )


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PaginateOrderingMixin():
    ordering = 'id'
    paginate_by = 10


class PostListView(PaginateOrderingMixin, ListView):
    model = Post
    template_name = 'blog/index.html'


class CategoryPostListView(
    MultipleObjectMixin,
    PaginateOrderingMixin,
    DetailView
):
    model = Category
    slug_url_kwarg = 'category_slug'
    template_name = 'blog/category.html'

    def get_context_data(self, **kwargs):
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        object_list = get_posts().filter(category=category)
        context = super(CategoryPostListView, self).get_context_data(
            object_list=object_list,
            **kwargs
        )
        context['category'] = category
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    # success_url = reverse_lazy("blog:post_detail")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            Comment.objects.select_related('author', 'post')
        )
        return context


class PostEditView(OnlyAuthorMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    form_class = PostForm


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    form_class = PostForm
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        context['form'] = PostForm(instance=post)
        return context


class ProfileDetailView(
    LoginRequiredMixin,
    MultipleObjectMixin,
    PaginateOrderingMixin,
    DetailView,
):
    model = User
    template_name = 'blog/profile.html'

    def get_object(self):
        pass

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs['username'])
        object_list = get_posts().filter(author=user)
        context = super(ProfileDetailView, self).get_context_data(
            object_list=object_list,
            **kwargs
        )
        context['profile'] = user
        print(context)
        return context


class ProfileUpdateView(OnlyAuthorMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = UserForm


class CommentCreateView(LoginRequiredMixin, CreateView):
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
        return reverse('blog:post_detail', kwargs={'post_id': self.post_card.pk})


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    form_class = CommentForm

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})

class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    form_class = CommentForm
    
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


def index(request):
    """Главная страница"""
    template = 'blog/index.html'
    context = {
        'post_list': get_posts()[:POSTS_PER_PAGE],
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Полный пост"""
    template = 'blog/detail.html'
    context = {
        'post': get_object_or_404(
            get_posts(),
            id=post_id
        )
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    """Описание категории поста"""
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    context = {
        'category': category,
        'post_list': get_posts().filter(category=category)
    }
    return render(request, template, context)
