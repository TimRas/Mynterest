from django import forms
from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('topic', 'title', 'content', 'excerpt',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
