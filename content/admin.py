from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Post, Comment, Topic


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):

    prepopulated_fields = {'slug': ('title',)}
    summernote_fields = ('content', 'excerpt')
    list_filter = ('created_date',)
    search_fields = ['title', 'content']
    list_display = ('title', 'author', 'topic', 'created_date')


@admin.register(Comment)
class CommentAdmin(SummernoteModelAdmin):

    summernote_fields = ('body')
    list_filter = ('created_date',)
    search_fields = ['body']
    list_display = ('author', 'post', 'body', 'created_date')


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title']
    list_display = ('title',)