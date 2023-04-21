from django.test import TestCase
from django.db import IntegrityError
from datetime import datetime
from .models import Topic, Post, Comment, User
 

class TopicModelTest(TestCase):
    """" Test class for Topic model. Checks if title field requirements work properly """

    @classmethod
    def setUpTestData(cls):
        Topic.objects.create(title='Test Topic')

    def test_title_field_filled_required(self):
        topic = Topic.objects.get(id=1)
        self.assertEqual(topic.title, 'Test Topic')

    def test_title_field_unique(self):
        with self.assertRaises(IntegrityError):
            Topic.objects.create(title='Test Topic')


class PostModelTest(TestCase):
    """" Test class for Post model. Checks if several field requirements work properly """

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='testuser')
        topic = Topic.objects.create(title='Test Topic')
        Post.objects.create(topic=topic, title='Test Post', author=user, content='Test content', excerpt='Test excerpt')

    def test_title_field_filled_in(self):
        post = Post.objects.get(id=1)
        self.assertEqual(post.title, 'Test Post')

    def test_content_field_filled_in(self):
        post = Post.objects.get(id=1)
        self.assertEqual(post.content, 'Test content')

    def test_excerpt_field_filled_in(self):
        post = Post.objects.get(id=1)
        self.assertEqual(post.excerpt, 'Test excerpt')


