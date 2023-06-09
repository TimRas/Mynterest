from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from cloudinary.models import CloudinaryField


class Topic(models.Model):  
    title = models.CharField(max_length=70, unique=True, null=False, blank=False)
    slug = models.SlugField(max_length=70, unique=True)
    image = CloudinaryField('image', default='placeholder')

    def __str__(self):
        return str(self.title)
    

class Post(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=70, unique=True, null=False, blank=False)
    slug = models.SlugField(max_length=70)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_posts')
    content = models.TextField(max_length=500, null=False, blank=False)
    image = CloudinaryField('image', default='placeholder')
    excerpt = models.TextField(max_length=100, null=False, blank=False)
    created_date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='post_likes', blank=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return str(self.title)

    def save(self, *args, **kwargs):   
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def amount_of_likes(self):
        return self.likes.count()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    body = models.TextField(max_length=250, null=False, blank=False)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_date']

    def __str__(self):
        return f'Comment {self.body} by {self.author}'
