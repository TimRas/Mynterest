from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from .models import Topic, Post, Comment
from .forms import CommentForm, PostForm


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_login(self.user)
        self.topic = Topic.objects.create(title="New Topic", slug="new-topic")
        self.post = Post.objects.create(
            topic=self.topic,
            title="Test Title",
            content="Test Content",
            excerpt="Test Excerpt",
            author=self.user,
            slug=slugify("Test Title")
        )

        self.comment = Comment.objects.create(
            post=self.post,
            body="Test Comment",
            author=self.user,
        )

    def test_topic_list_view(self):
        """ Test to see if homepage is loading correctly """
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_post_list_view(self):
        """ Test to see if the posts are loading correctly """
        
        response = self.client.get(reverse("posts", kwargs={"topic": self.topic.slug}))
        self.assertEqual(response.status_code, 200)

    def test_post_detail_view(self):
        """ Test to see if the post detail page is loading correctly """

        response = self.client.get(reverse("post_detail", kwargs={"slug": self.post.slug}))
        self.assertEqual(response.status_code, 200)

    def test_post_list_post_valid_form(self):
        """Test to see if a post can be made with a valid form"""

        self.client.force_login(self.user)

        post_data = {
            "topic": self.topic.id,
            "title": "test title",
            "content": "test content",
            "excerpt": "test excerpt",
        }

        response = self.client.post(
            reverse("posts", kwargs={"topic": self.topic.slug}),
            data=post_data,
            follow=True
        )

        post = Post.objects.latest("id")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(post.title, post_data["title"])
        self.assertEqual(post.content, post_data["content"])
        self.assertEqual(post.excerpt, post_data["excerpt"])
        self.assertEqual(post.topic, self.topic)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.slug, slugify(self.post.title))


    def test_post_list_post_invalid_form(self):
        """ Test to see if with a invalid form, a post can't be created """

        self.client.force_login(self.user)

        post_data = {
            "topic": self.topic,
            "title": "",
            "content": "",
            "excerpt": "",
        }
        post_form = PostForm(data=post_data)
        self.assertFalse(post_form.is_valid())

        self.assertTrue("title" in post_form.errors)
        self.assertTrue("content" in post_form.errors)
        self.assertTrue("excerpt" in post_form.errors)

        response = self.client.post(
            reverse("posts", kwargs={"topic": self.topic.slug}),
            data=post_data,
        )

        self.assertFalse(Post.objects.filter(title=post_data["title"]).exists())
        self.assertEqual(response.status_code, 200)

    def test_post_detail_post_valid_form(self):
        """" Test to see if a comment can be made with a valid form """

        self.client.force_login(self.user)

        comment_data = {
            "body": "test comment",
        }

        comment_form = CommentForm(data=comment_data)
        self.assertTrue(comment_form.is_valid())
        comment = comment_form.save(commit=False)
        comment.post = self.post
        comment.author = self.user
        comment.created_date=timezone.now()
        comment.save()

        response = self.client.post(
            reverse("post_detail", kwargs={"slug": self.post.slug}),
            data=comment_data,
        )

        self.assertEqual(response.status_code, 200)

        comment = Comment.objects.last()

        self.assertEqual(comment.body, comment_data["body"])
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)
        self.assertIsNotNone(comment.created_date)
        
        response = self.client.get(reverse("post_detail", kwargs={"slug": self.post.slug}))
        self.assertContains(response, comment.body)

    def test_post_detail_post_invalid_form(self):
        """ Test to see if with a invalid form, a comment can't be created """
        
        self.client.force_login(self.user)

        comment_data = {
            "content": "",
        }
        response = self.client.post(
            reverse("post_detail", kwargs={"slug": self.post.slug}),
            data=comment_data,
        )
        self.assertFalse(Comment.objects.filter(body=comment_data["content"]).exists())
        self.assertEqual(response.status_code, 200)

    def test_get_edit_post_form(self):
        """Test the GET request to the edit post form"""

        response = self.client.get(reverse("edit_post", kwargs={"slug": self.post.slug}))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.content)
        self.assertContains(response, self.post.excerpt)

    def test_post_edit_post_form_valid(self):
        """Test the POST request to edit a post with a valid form"""

        post_data = {
            "topic": self.topic.id,
            "title": "Updated Title",
            "content": "Updated Content",
            "excerpt": "Updated Excerpt",
        }

        response = self.client.post(reverse("edit_post", kwargs={"slug": self.post.slug}), data=post_data)

        post = Post.objects.latest("id")

        self.assertEqual(response.status_code, 200)

        self.assertEqual(post_data["title"], post.title)
        self.assertEqual(post_data["content"], post.content)
        self.assertEqual(post_data["excerpt"], post.excerpt)

    def test_post_edit_post_form_invalid(self):
        """Test the POST request to edit a post with an invalid form"""

        invalid_post_data = {
            "topic": self.topic.id,
            "title": "", 
            "content": "Updated Content",
            "excerpt": "Updated Excerpt",
        }

        response = self.client.post(reverse("edit_post", kwargs={"slug": self.post.slug}), data=invalid_post_data)

        self.assertEqual(response.status_code, 200)

        self.assertNotEqual(self.post.title, invalid_post_data["title"])
        self.assertNotEqual(self.post.content, invalid_post_data["content"])
        self.assertNotEqual(self.post.excerpt, invalid_post_data["excerpt"])

    def test_get_edit_comment_form(self):
        """Test the GET request to the edit comment form"""

        response = self.client.get(reverse("edit_comment", kwargs={"comment_id": self.comment.id}))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.comment.body)

    def test_post_edit_comment_form_valid(self):
        """Test the POST request to edit a comment with a valid form"""

        comment_data = {
            "body": "Updated Comment",
        }

        response = self.client.post(reverse("edit_comment", kwargs={"comment_id": self.comment.id}), data=comment_data)

        self.assertEqual(response.status_code, 302) 

        comment = Comment.objects.latest("id")

        self.assertEqual(comment.body, comment_data["body"])

    def test_post_edit_comment_form_invalid(self):
        """Test the POST request to edit a comment with an invalid form"""

        invalid_comment_data = {
            "body": "", 
        }

        response = self.client.post(reverse("edit_comment", kwargs={"comment_id": self.comment.id}),
                                    data=invalid_comment_data)

        self.assertEqual(response.status_code, 302)

        self.assertNotEqual(self.comment.body, invalid_comment_data["body"])

    def test_post_like(self):
        """Test liking a post"""
        self.client.force_login(self.user)
    
        response = self.client.post(reverse('post_like', args=[self.post.slug]))
        
        self.assertEqual(response.status_code, 302)
        
        self.assertIn(self.user, self.post.likes.all())

    def test_post_unlike(self):
        """Test unliking a post"""
        self.client.force_login(self.user)
        
        self.post.likes.add(self.user)
    
        response = self.client.post(reverse('post_like', args=[self.post.slug]))
        
        self.assertEqual(response.status_code, 302)
        
        self.assertNotIn(self.user, self.post.likes.all())

    def test_delete_post(self):
        """Test deleting a post"""
        self.client.force_login(self.user)
        
        response = self.client.get(reverse('delete_post', args=[self.post.slug]))
        
        self.assertEqual(response.status_code, 302)
        
        self.assertFalse(Post.objects.filter(slug=self.post.slug).exists())

        self.assertNotIn(self.post, self.post.topic.posts.all())

    def test_delete_comment(self):
        """Test deleting a comment"""
        self.client.force_login(self.user)

        response = self.client.get(reverse('delete_comment', args=[self.comment.id]))

        self.assertEqual(response.status_code, 302)

        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

        self.assertNotIn(self.comment, self.post.comments.all())

