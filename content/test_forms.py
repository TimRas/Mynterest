from django.test import TestCase
from django.contrib.auth import get_user_model
from .forms import CommentForm, PostForm
from .models import Topic

User = get_user_model()


class TestForms(TestCase):

    def test_comment_form_valid_data(self):
        """"
        Test to see if comment form is valid with valid data
        and that the comment can be saved with the valid data.
        """

        user = User.objects.create_user(username='testuser', password='12345')
        topic = Topic.objects.create(title="example", slug="example")
        post = topic.posts.create(title="test post", content="test content",
                                  excerpt="excerpt", author=user)
        form = CommentForm(data={'body': 'test comment'})
        self.assertTrue(form.is_valid())
        comment = form.save(commit=False)
        comment.post = post
        comment.author = user
        comment.save()
        self.assertEqual(comment.body, 'test comment')

    def test_comment_form_empty_data(self):
        """
        Test to see if the comment form is invalid
        when provided with zero data.
        """

        form = CommentForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)

    def test_post_form_valid_data(self):
        """
        Test to see if post form is valid with valid data
        and that the post can be saved with the valid data.
        """

        user = User.objects.create_user(username='testuser', password='12345')
        topic = Topic.objects.create(title="example", slug="example")
        form = PostForm(data={
            'title': 'test title',
            'excerpt': 'test excerpt',
            'content': 'test content'
        })
        self.assertTrue(form.is_valid())
        post = form.save(commit=False)
        post.author = user
        post.topic = topic
        post.save()
        self.assertEqual(post.title, 'test title')

    def test_post_form_empty_data(self):
        """
         Test to see if the post form is invalid
         when provided with zero data.
         """

        form = PostForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)
