from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import DateTimeInput

from .models import Post, Comment


class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        widget=DateTimeInput(
            attrs={
                'type': 'datetime-local'
            }
        )
    )

    class Meta:
        model = Post
        exclude = ('author',)


class DeletePostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', )


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text', )
