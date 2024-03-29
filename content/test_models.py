from django.test import TestCase
from django.db import IntegrityError
from .models import Topic, Post, Comment, User


class TopicModelTest(TestCase):
    """
    Test class for Topic model.
    Checks if title field requirements work properly.
    """

    def setUp(self):
        self.topic = Topic.objects.create(title='Test Topic',
                                          slug='test-topic')

    def test_title_field_filled_required(self):
        topic = Topic.objects.get(id=1)
        self.assertEqual(topic.title, 'Test Topic')

    def test_title_field_unique(self):
        with self.assertRaises(IntegrityError):
            Topic.objects.create(title='Test Topic')


class PostModelTest(TestCase):
    """
    Test class for Post model.
    Checks if several field requirements work properly
    and if __str__ and amount of likes method work properly.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             password='testpassword')
        self.topic = Topic.objects.create(title='Test Topic',
                                          slug='test-topic')
        self.post = Post.objects.create(
            topic=self.topic,
            title='Test Post',
            author=self.user,
            content='Test content',
            excerpt='Test excerpt'
        )
        self.post.likes.add(self.user)

    def test_topic_field_filled(self):
        post = Post.objects.get(id=1)
        self.assertEqual(str(post.topic), 'Test Topic')

    def test_title_field_filled_in(self):
        post = Post.objects.get(id=1)
        self.assertEqual(post.title, 'Test Post')

    def test_content_field_filled_in(self):
        post = Post.objects.get(id=1)
        self.assertEqual(post.content, 'Test content')

    def test_excerpt_field_filled_in(self):
        post = Post.objects.get(id=1)
        self.assertEqual(post.excerpt, 'Test excerpt')

    def test_str_method(self):
        expected_str = self.post.title
        self.assertEqual(str(self.post), expected_str)

    def test_amount_of_likes(self):
        expected_likes_count = 1
        self.assertEqual(self.post.amount_of_likes(), expected_likes_count)


class CommentModelTest(TestCase):
    """
    Test class for comment model.
    Checks if __str__ method is able to print the proper values.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             password='testpassword')
        self.topic = Topic.objects.create(title='Test Topic',
                                          slug='test-topic')
        self.post = Post.objects.create(
            topic=self.topic,
            title='Test Post',
            author=self.user,
            content='Test content',
            excerpt='Test excerpt'
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            body='Test comment body'
        )

    def test_str_method(self):
        expected_str = f'Comment {self.comment.body} by {self.comment.author}'
        self.assertEqual(str(self.comment), expected_str)
