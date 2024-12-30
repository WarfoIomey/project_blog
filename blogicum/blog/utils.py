from datetime import datetime

from .models import Post


def get_posts():
    """Получение постов"""
    now = datetime.today()
    return Post.objects.select_related(
        'location', 'author', 'category'
    ).filter(
        is_published=True,
        pub_date__lt=now,
        category__is_published=True
    ).order_by('-pub_date')
