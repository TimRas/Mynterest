from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Post, Comment, Topic


@admin.register(Post, Comment, Topic)
class PostandCommentAdmin(SummernoteModelAdmin):

    summernote_fields = ('content', 'body')
