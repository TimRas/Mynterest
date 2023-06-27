from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from .models import Topic, Post, Comment
from .forms import CommentForm, PostForm


class TestViews(TestCase):

    def setUp(self):
        """ Setup to run tests. """
        self.client = Client()
        self.user = User.objects.create_user(username='testuser',
                                             password='12345')
        self.user2 = User.objects.create_user(username='testuser2',
                                              password='123456')
        self.client.force_login(self.user)
        self.topic = Topic.objects.create(title="New Topic",
                                          slug="new-topic")
        self.post2 = Post.objects.create(
            topic=self.topic,
            title="Test Title2",
            content="Test Content2",
            excerpt="Test Excerpt2",
            author=self.user
        )

        self.post2.likes.set([self.user, self.user2])

        self.post = Post.objects.create(
            topic=self.topic,
            title="Test Title",
            content="Test Content",
            excerpt="Test Excerpt",
            author=self.user
        )

        self.post.likes.set([self.user])

        self.comment = Comment.objects.create(
            post=self.post,
            body="Test Comment",
            author=self.user,
        )

    def test_topic_list_view(self):
        """ Test to see if homepage is loading correctly. """
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_most_liked_posts(self):
        """ Test if only post with the most likes return. """
        url = reverse('posts', kwargs={'topic': self.topic.slug})
        response = self.client.get(f"{url}?most_liked=true")

        first_post = response.context['posts'][0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(first_post.title, "Test Title2")

    def test_all_posts(self):
        """
        Test to check that all posts are displayed
        correctly for their given topic.
        """
        url = reverse('posts', kwargs={'topic': self.topic.slug})
        response = self.client.get(url)

        first_post = response.context['posts'][0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(first_post.title, "Test Title")

    def test_unauthenticated_user(self):
        """
        Test to check behaviour if unauthenticated user
        tries to use the create post button/functionality.
        """
        self.client.logout()
        url = reverse('check_can_post', kwargs={'topic': self.topic.slug})
        response = self.client.get(url)

        self.assertRedirects(response, reverse('account_login'))
        storage = get_messages(response.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn("You need to sign in or register to create a post",
                      messages)

    def test_authenticated_user(self):
        """
        Test to check behaviour if authenticated user
        tries to use the create post button/functionality.
        """
        url = reverse('check_can_post', kwargs={'topic': self.topic.slug})
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertRedirects(response, reverse('create_post',
                             kwargs={'topic': self.topic.slug}))

    def test_post_method_not_allowed(self):
        """
        Test to check if HttpResponseNotAllowed
        for the POST method can be triggered.
        """
        url = reverse('check_can_post', kwargs={'topic': self.topic.slug})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 405)

    def test_post_detail_view(self):
        """ Test to see if the post detail page is loading correctly. """

        response = self.client.get(reverse("post_detail",
                                   kwargs={"slug": self.post.slug}))
        self.assertEqual(response.status_code, 200)

    def test_get_request(self):
        """
        Test to check if the GET request for the post details page
        is working properly and if the form is rendered correctly.
        """
        url = reverse("create_post", kwargs={"topic": self.topic.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        post_form = response.context['post_form']
        self.assertIsInstance(post_form, PostForm)
        self.assertEqual(post_form.initial['topic'], self.topic)

    def test_valid_post_request(self):
        """
        Test to check if a valid form is successfully posted
        and if the post is found in the database with the correct values.
        """
        url = reverse("create_post", kwargs={"topic": self.topic.slug})

        post_data = {
            "topic": self.topic.id,
            "title": "Test Title3",
            "content": "Test Content3",
            "excerpt": "Test Excerpt3",
        }

        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        post = Post.objects.latest("created_date")
        self.assertEqual(post.title, post_data["title"])
        self.assertEqual(post.content, post_data["content"])
        self.assertEqual(post.excerpt, post_data["excerpt"])
        self.assertEqual(post.topic, self.topic)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.slug, slugify(post.title + '_' + str(post.uuid),
                         allow_unicode=True))

    def test_invalid_post_request(self):
        """ Test to check that an invalid post from can't be posted. """
        url = reverse("create_post", kwargs={"topic": self.topic.slug})

        post_data = {
            "topic": "",
            "title": "",
            "content": "",
            "excerpt": "",
        }

        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 200)

    def test_post_detail_post_valid_form(self):
        """" Test to see if a comment can be made with a valid form. """

        self.client.force_login(self.user)

        comment_data = {
            "body": "test comment",
        }

        comment_form = CommentForm(data=comment_data)
        self.assertTrue(comment_form.is_valid())
        comment = comment_form.save(commit=False)
        comment.post = self.post
        comment.author = self.user
        comment.created_date = timezone.now()
        comment.save()

        response = self.client.post(
            reverse("post_detail", kwargs={"slug": self.post.slug}),
            data=comment_data,
        )

        self.assertEqual(response.status_code, 302)

        comment = Comment.objects.last()

        self.assertEqual(comment.body, comment_data["body"])
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)
        self.assertIsNotNone(comment.created_date)
        response = self.client.get(reverse("post_detail",
                                   kwargs={"slug": self.post.slug}))
        self.assertContains(response, comment.body)

    def test_post_detail_post_invalid_form(self):
        """ Test to see if with a invalid form, a comment can't be created. """

        self.client.force_login(self.user)

        comment_data = {
            "content": "",
        }
        response = self.client.post(
            reverse("post_detail", kwargs={"slug": self.post.slug}),
            data=comment_data,
        )
        self.assertFalse(Comment.objects.filter
                         (body=comment_data["content"]).exists())
        self.assertEqual(response.status_code, 200)

    def test_get_edit_post_form(self):
        """ Test the GET request to the edit post form. """

        response = self.client.get(reverse("edit_post",
                                   kwargs={"slug": self.post.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.content)
        self.assertContains(response, self.post.excerpt)

    def test_post_edit_post_form_valid(self):
        """ Test the POST request to edit a post with a valid form. """

        post_data = {
            "topic": self.topic.id,
            "title": "Updated Title",
            "content": "Updated Content",
            "excerpt": "Updated Excerpt",
        }

        response = self.client.post(reverse("edit_post",
                                    kwargs={"slug": self.post.slug}),
                                    data=post_data)

        post = Post.objects.latest("id")

        self.assertEqual(response.status_code, 200)

        self.assertEqual(post_data["title"], post.title)
        self.assertEqual(post_data["content"], post.content)
        self.assertEqual(post_data["excerpt"], post.excerpt)

    def test_post_edit_post_form_invalid(self):
        """ Test the POST request to edit a post with an invalid form. """

        invalid_post_data = {
            "topic": self.topic.id,
            "title": "",
            "content": "Updated Content",
            "excerpt": "Updated Excerpt",
        }

        response = self.client.post(reverse("edit_post",
                                    kwargs={"slug": self.post.slug}),
                                    data=invalid_post_data)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.post.title, invalid_post_data["title"])
        self.assertNotEqual(self.post.content, invalid_post_data["content"])
        self.assertNotEqual(self.post.excerpt, invalid_post_data["excerpt"])

    def test_get_edit_comment_form(self):
        """ Test the GET request to the edit comment form. """

        response = self.client.get(reverse("edit_comment",
                                   kwargs={"comment_id": self.comment.id}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.comment.body)

    def test_post_edit_comment_form_valid(self):
        """ Test the POST request to edit a comment with a valid form. """

        comment_data = {
            "body": "Updated Comment",
        }

        response = self.client.post(reverse("edit_comment",
                                    kwargs={"comment_id": self.comment.id}),
                                    data=comment_data)

        self.assertEqual(response.status_code, 302)

        comment = Comment.objects.latest("id")

        self.assertEqual(comment.body, comment_data["body"])

    def test_post_edit_comment_form_invalid(self):
        """ Test the POST request to edit a comment with an invalid form. """

        invalid_comment_data = {
            "body": "",
        }

        response = self.client.post(reverse("edit_comment",
                                    kwargs={"comment_id": self.comment.id}),
                                    data=invalid_comment_data)

        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(self.comment.body, invalid_comment_data["body"])

    def test_post_like(self):
        """ Test liking a post. """
        self.post.likes.set([])
        self.client.force_login(self.user)

        response = self.client.post(reverse('post_like',
                                    args=[self.post.slug]))
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.user, post.likes.all())

    def test_post_unlike(self):
        """ Test unliking a post. """
        self.client.force_login(self.user)
        self.post.likes.add(self.user)
        response = self.client.post(reverse('post_like',
                                    args=[self.post.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.user, self.post.likes.all())

    def test_unauthenticated_like(self):
        """
        Test to check if behaviour if unauthenticated user tries to like.
        That he will be redirected to the login page
        and that the error message will be shown.
        """
        self.client.logout()
        url = reverse('check_like_post', kwargs={'slug': self.post.slug})
        response = self.client.get(url)

        self.assertRedirects(response, reverse('account_login'))
        storage = get_messages(response.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn("You need to sign in or register to like a post",
                      messages)

    def test_authenticated_like(self):
        """
        Test to check if behaviour if authenticated user tries to like.
        That he will be redirected to the post details page of given post.
        """
        url = reverse('check_like_post', kwargs={'slug': self.post.slug})
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertRedirects(response, reverse('post_detail',
                             kwargs={'slug': self.post.slug}))

    def test_post_method_not_allowed_like(self):
        """
        Test to check if HttpResponseNotAllowed
        for the POST method can be triggered if the user is unauthenticated.
        """
        url = reverse('check_like_post', kwargs={'slug': self.post.slug})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 405)

    def test_delete_post(self):
        """Test deleting a post"""

        self.client.force_login(self.user)
        response = self.client.get(reverse('delete_post',
                                           args=[self.post.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(slug=self.post.slug).exists())
        self.assertNotIn(self.post, self.post.topic.posts.all())

    def test_delete_comment(self):
        """Test deleting a comment"""

        self.client.force_login(self.user)

        response = self.client.get(reverse('delete_comment',
                                           args=[self.comment.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())
        self.assertNotIn(self.comment, self.post.comments.all())

    def test_delete_comment_authorization_failed(self):
        """
        Test the authorization failed if
        an unauthenticated user tries to delete a comment.
        """
        self.client.logout()

        url = reverse('delete_comment', kwargs={'comment_id': self.comment.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "POST")

    def test_post_list_get_exception(self):
        """ Test the exception handling for PostList view get method. """
        url = reverse("posts", kwargs={"topic": "non-existent-topic"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_post_detail_get_exception(self):
        """ Test the exception handling for PostDetail view get method. """
        url = reverse("post_detail", kwargs={"slug": "non-existent-slug"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_post_detail_post_exception(self):
        """ Test the exception handling for PostDetail view post method. """
        url = reverse("post_detail", kwargs={"slug": "non-existent-slug"})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)

    def test_create_post_get_exception(self):
        """ Test the exception handling for CreatePost view get method. """
        url = reverse("create_post", kwargs={"topic": "non-existent-topic"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_create_post_post_exception(self):
        """ Test the exception handling for CreatePost view post method. """
        url = reverse("create_post", kwargs={"topic": "non-existent-topic"})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        storage = get_messages(response.wsgi_request)
        messages = [message.message for message in storage]
        self.assertIn("Form is invalid. No Topic matches the given query.",
                      messages)

    def test_edit_post_get_exception(self):
        """ Test the exception handling for EditPost view get method. """
        url = reverse("edit_post", kwargs={"slug": "non-existent-slug"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_edit_post_post_exception(self):
        """ Test the exception handling for EditPost view post method. """
        url = reverse("edit_post", kwargs={"slug": "non-existent-slug"})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)

    def test_edit_comment_get_exception(self):
        """ Test the exception handling for EditComment view get method. """
        url = reverse("edit_comment", kwargs={"comment_id": 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_edit_comment_post_exception(self):
        """ Test the exception handling for EditComment view post method. """
        url = reverse("edit_comment", kwargs={"comment_id": 99999})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)

    def test_post_like_post_exception(self):
        """ Test the exception handling for PostLike view post method. """
        url = reverse("post_like", kwargs={"slug": "non-existent-slug"})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)

    def test_delete_post_get_exception(self):
        """ Test the exception handling for DeletePost view get method. """
        url = reverse("delete_post", kwargs={"slug": "non-existent-slug"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_delete_comment_get_exception(self):
        """ Test the exception handling for DeleteComment view get method. """
        url = reverse("delete_comment", kwargs={"comment_id": 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
