from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse, reverse_lazy


User = get_user_model()


class PublishedAndCreatTimeModel(models.Model):
    """Абстрактная модель. Добвляет флаг is_published и created_at"""

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Время создания записи',
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class Post(PublishedAndCreatTimeModel):
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
        help_text='Название поста, максимальная длинна строки 256'
    )
    text = models.TextField(
        help_text='Текст поста',
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату и время в будущем'
                   ' — можно делать отложенные публикации.')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        help_text='Автор поста',
        related_name='posts',
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        verbose_name='Местоположение',
        null=True,
        blank=True,
        help_text='Место'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        help_text='Категория поста',
        null=True
    )
    image = models.ImageField(
        'Фото',
        upload_to='posts_images',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return f'{self.title} - {self.created_at}'

    @property
    def comment_count(self):
        return self.comments.count()

    def get_absolute_url(self):
        return reverse('blog:index')


class Category(PublishedAndCreatTimeModel):
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
        help_text='Название категории, максимальная длинна строки 256'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=('Идентификатор страницы для URL;'
                   ' разрешены символы латиницы, цифры, дефис'
                   ' и подчёркивание.')
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedAndCreatTimeModel):
    name = models.CharField(
        max_length=256,
        verbose_name='Название места',
        help_text='Место, максимальная длинна строки 256'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Comment(models.Model):
    text = models.TextField(
        help_text='Текст комментария',
        verbose_name='Текст'
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        verbose_name='пост',
        help_text='Комментарий поста',
        null=True,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        help_text='Автор комментария',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Время создания записи',
        verbose_name='Добавлено'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author.username} - {self.text}'
