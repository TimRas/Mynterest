from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=70, unique=True)
    slug = models.SlugField(max_length=70, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_posts')
    content = models.TextField()
    image = models.URLField(max_length=200)
    excerpt = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='post_likes', blank=True)


    class Meta:
        ordering = ['-created_date']


    def __str__(self):
        return str(self.title)


    def amount_of_likes(self):
        return self.likes.count()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    body = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='comment_likes', blank=True)


    class Meta:
        ordering = ['created_date']


    def __str__(self):
        return f'Comment {self.body} by {self.author}'


# will add amount of posts and amount of comments and admin use only
class Topic(models.Model):
    title = models.CharField(max_length=70, unique=True)
    image = models.URLField(max_length=200)
    
    