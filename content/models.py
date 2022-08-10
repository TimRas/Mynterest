from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=70, unique=True)
    slug = models.SlugField(max_length=70, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_posts')
    content = models.TextField()
    image = models.URLField(max_length=200, blank=True)
    excerpt = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='post_likes', blank=True)
    dislikes = models.ManyToManyField(User, related_name='post_dislikes', blank=True)


    class Meta:
        ordering = ['-created_date']


    def __str__(self):
        return str(self.title)


    def amount_of_likes(self):
        return self.likes.count()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    title = models.CharField(max_length=70, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    body = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='comment_likes', blank=True)
    dislikes = models.ManyToManyField(User, related_name='comment_dislikes', blank=True)

    class Meta:
        ordering = ['created_date']


    def __str__(self):
        return str(self.title)


    def __str__(self):
        return f'Comment {self.body} by {self.author}'



class Topic(models.Model):
    title = models.CharField(max_length=70, unique=True)
    slug = models.SlugField(max_length=70, unique=True)
    image = models.URLField(max_length=200, blank=True)
    amount_of_posts = models.ManyToManyField(User, related_name='all_posts', blank=True)
    amount_of_comments = models.ManyToManyField(User, related_name='all_comments', blank=True)

    def __str__(self):
        return str(self.title)

    def amount_of_posts_in_total(self):
        return self.amount_of_posts.count()

    def amount_of_comments_in_total(self):
        return self.amount_of_comments.count()