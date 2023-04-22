from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from .models import Topic, Post, Comment, User


class TestViews(TestCase):

    def test_topic_list_view(self):
        """ Test to see if homepage is loading correctly """
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_post_list_view(self):
        """ Test to see if the posts are loading correctly """

        topic = Topic.objects.create(title="example", slug="example")
        response = self.client.get(reverse("posts", kwargs={"topic": topic.slug}))
        self.assertEqual(response.status_code, 200)

    def test_post_detail_view(self):
        """ Test to see if the post detail page is loading correctly """

        user = User.objects.create_user(username='testuser', password='12345')
        topic = Topic.objects.create(title='test topic')
        post = Post.objects.create(title="test post", content="test content", author=user, topic=topic)
        response = self.client.get(reverse("post_detail", kwargs={"slug": post.slug}))
        self.assertEqual(response.status_code, 200)

    def test_post_list_post_valid_form(self):
        """" Test to see if a post can be made with a valid form """

        user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_login(user)
        topic = Topic.objects.create(title="example", slug="example")
        post_data = {
            "title": "test title",
            "content": "test content",
        }
        Post.objects.create(topic=topic, author=user, **post_data)
        response = self.client.post(
            reverse("posts", kwargs={"topic": topic.slug}),
            data=post_data,
        )
        self.assertTrue(Post.objects.filter(title=post_data["title"]).exists())
        self.assertEqual(response.status_code, 200)

    def test_post_list_post_invalid_form(self):
        """ Test to see if with a invalid form, a post can't be created """

        user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_login(user)
        topic = Topic.objects.create(title="example", slug="example")
        post_data = {
            "title": "",
            "content": "",
        }
        response = self.client.post(
            reverse("posts", kwargs={"topic": topic.slug}),
            data=post_data,
        )
        self.assertFalse(Post.objects.filter(title=post_data["title"]).exists())
        self.assertEqual(response.status_code, 200)

    def test_post_detail_post_valid_form(self):
        """" Test to see if a comment can be made with a valid form """

        user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_login(user)
        topic = Topic.objects.create(title='test topic')
        post = Post.objects.create(title="test post", content="test content", author=user, topic_id=topic.id)
        comment_data = {
            "content": "test comment",
        }
        response = self.client.post(
            reverse("post_detail", kwargs={"slug": post.slug}),
            data=comment_data,
        )
        comment = Comment.objects.create(
            body=comment_data['content'],
            post=post,
            author=user,
            created_date=timezone.now()
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("post_detail", kwargs={"slug": post.slug}))
        self.assertContains(response, comment.body)

    def test_post_detail_post_invalid_form(self):
        """ Test to see if with a invalid form, a comment can't be created """
        
        user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_login(user)
        topic = Topic.objects.create(title='test topic')
        post = Post.objects.create(title="test post", content="test content", author=user, topic_id=topic.id)
        comment_data = {
            "content": "",
        }
        response = self.client.post(
            reverse("post_detail", kwargs={"slug": post.slug}),
            data=comment_data,
        )
        self.assertFalse(Comment.objects.filter(body=comment_data["content"]).exists())
        self.assertEqual(response.status_code, 200)
