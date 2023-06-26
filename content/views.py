from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.views import View, generic
from django.http import HttpResponseRedirect
from django.db.models import Count
from .models import Topic, Post, Comment
from .forms import CommentForm, PostForm


class TopicList(generic.ListView):
    """ Displays a list of all topics """

    model = Topic
    queryset = Topic.objects.all()
    template_name = "index.html"


class PostList(View):
    """
    Renders all all posts related to the given topic.
    Validates the submitted form, saves the new post in the database
    and redirects the user back to the post page
    with the given topic and handles the most-liked functionality
    """

    def get(self, request, topic, *args, **kwargs):
        try:
            get_object_or_404(Topic, slug=topic)
            queryset = Post.objects.filter(topic__slug=topic)
            most_liked = request.GET.get('most_liked', False) == 'true'

            if most_liked:
                queryset = (
                    queryset
                    .annotate(num_likes=Count('likes'))
                    .filter(num_likes__gt=0)
                    .order_by('-num_likes')
                    [:5]
                )
            else:
                queryset = Post.objects.filter(topic__slug=topic)

            paginator = Paginator(queryset, 6)
            page_number = request.GET.get('page')
            posts = paginator.get_page(page_number)
            topic = self.kwargs['topic']

            return render(
                request,
                "posts.html",
                {
                    "posts": posts,
                    "topic": topic,
                    "most_liked": most_liked,
                },
            )
        except Exception as exception:
            raise type(exception)(str(exception)) from exception


class AuthCheckPost(View):
    """
    Checks if user in logged in when trying to post.
    If not will redirect to login page else it will open up the post form.
    """

    def get(self, request, topic, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request,
                           "You need to sign in or register to create a post")
            return redirect('account_login')

        return redirect(reverse("create_post", kwargs={"topic": topic}))

    def post(self, *args, **kwargs):
        return HttpResponseNotAllowed(['GET'])


class PostDetail(View):
    """
    Renders post retreived form database and renders comment form.
    Validates the submitted form, saves the comment and
    redirects user to the details page of given post.
    """

    def get(self, request, slug, *args, **kwargs):
        queryset = Post.objects.all()
        try:
            post = get_object_or_404(queryset, slug=slug)
            topic = post.topic
            all_comments = post.comments.all().order_by("-created_date")

            paginator = Paginator(all_comments, 6)
            page_number = request.GET.get("page")
            comments = paginator.get_page(page_number)

            return render(
                request,
                "post_detail.html",
                {
                    "post": post,
                    "topic": topic,
                    "comments": comments,
                    "comment_form": CommentForm()
                },
            )
        except Exception as exception:
            raise type(exception)(str(exception)) from exception

    def post(self, request, slug, *args, **kwargs):
        try:
            post = get_object_or_404(Post, slug=slug)
            comments = post.comments.all().order_by("-created_date")
            comment_form = CommentForm(data=request.POST)

            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                messages.success(request,
                                 "Your comment has been added to the post!")
                return redirect("post_detail", slug=slug)
            else:
                comment_form = CommentForm()

            return render(
                request,
                "post_detail.html",
                {
                    "post": post,
                    "comments": comments,
                    "comment_form": comment_form,
                },
            )
        except Exception as exception:
            raise type(exception)(str(exception)) from exception


class AuthCheckLike(View):
    """
    Checks if user in logged in when trying to like.
    If not will redirect to login page else it will like the post.
    """

    def get(self, request, slug, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request,
                           "You need to sign in or register to like a post")
            return redirect('account_login')
        else:
            return redirect(reverse("post_detail", kwargs={"slug": slug}))

    def post(self, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'])


class CreatePost(View):
    """
    Render a post form in the given URL.
    Validate the submitted form, update the database
    and redirect to the given topic page.
    """

    def get(self, request, topic, *args, **kwargs):
        try:
            topic_field = get_object_or_404(Topic, slug=topic)
            post_form = PostForm(initial={"topic": topic_field})

            return render(request, "create_post.html",
                          {"topic": topic_field, "post_form": post_form})
        except Exception as exception:
            raise type(exception)(str(exception)) from exception

    def post(self, request, topic, *args, **kwargs):
        try:
            topic_field = get_object_or_404(Topic, slug=topic)
            post_form = PostForm(request.POST, request.FILES)

            if post_form.is_valid():
                post = post_form.save(commit=False)
                post.author = request.user
                post.topic = topic_field
                post.save()

                messages.success(request, "Your post has been created")
                return redirect(reverse("posts", kwargs={"topic": topic}))
            else:
                raise Exception()
        except Exception as exception:
            messages.error(request, f'Form is invalid. {exception}')
            return HttpResponse()


class EditPost(View):
    """
    Render a form in the edit post html of the given post.
    Validates the submitted form, update in the database
    and redirects to the given topic page.
    """

    def get(self, request, slug, *args, **kwargs):
        try:
            post = get_object_or_404(Post, slug=slug)
            post_form = PostForm(instance=post)

            return render(request, "edit_post.html",
                          {"post_form": post_form, "post": post})
        except Exception as exception:
            raise type(exception)(str(exception)) from exception

    def post(self, request, slug, *args, **kwargs):
        try:
            post = get_object_or_404(Post, slug=slug)
            post_form = PostForm(request.POST, instance=post)

            if post_form.is_valid():
                post_form.instance.name = request.user.username
                post_form.save()
                post_form = PostForm()
                messages.success(request,
                                 "Your post has been edited!")
            else:
                post_form = PostForm(request.POST, instance=post)

            posts = Post.objects.filter(topic__slug=post.topic.slug)

            return render(
                request,
                "posts.html",
                {
                    "posts": posts,
                    "post_form": post_form,
                    "topic": post.topic.slug,
                },
            )
        except Exception as exception:
            raise type(exception)(str(exception)) from exception


class EditComment(View):
    """
    Renders a form in the edit comment html of the given comment.
    validates the submitted form, update in the database
    and redirects to the post the comments belongs to.
    """

    def get(self, request, comment_id, *args, **kwargs):
        try:
            comment = get_object_or_404(Comment, id=comment_id)
            comment_form = CommentForm(instance=comment)

            return render(request, "edit_comment.html",
                          {"comment_form": comment_form, "comment": comment})
        except Exception as exception:
            raise type(exception)(str(exception)) from exception

    def post(self, request, comment_id, *args, **kwargs):
        try:
            comment = get_object_or_404(Comment, id=comment_id)
            comment_form = CommentForm(request.POST, instance=comment)

            if comment_form.is_valid():
                comment_form.instance.name = request.user.username
                comment_form.save()
                comment_form = CommentForm()
                messages.success(request,
                                 "Your comment has been edited!")
            else:
                comment_form = CommentForm(request.POST, instance=comment)

            post = comment.post

            return redirect("post_detail", slug=post.slug)
        except Exception as exception:
            raise type(exception)(str(exception)) from exception


class PostLike(View):
    """ The functionality for liking and unliking posts"""

    def post(self, request, slug, *args, **kwargs):
        try:
            post = get_object_or_404(Post, slug=slug)

            if post.likes.filter(id=request.user.id).exists():
                post.likes.remove(request.user)
            else:
                post.likes.add(request.user)

            return HttpResponseRedirect(reverse('post_detail', args=[slug]))
        except Exception as exception:
            raise type(exception)(str(exception)) from exception


class DeletePost(View):
    """ Retrieves post and deletes it """

    def get(self, request, slug):
        try:
            post = get_object_or_404(Post, slug=slug)
            topic = post.topic.slug

            if request.user == post.author:
                post.delete()
                messages.success(request,
                                 "Your post has been deleted!")
                return redirect(reverse("posts", kwargs={"topic": topic}))

        except Exception as exception:
            raise type(exception)(str(exception)) from exception


class DeleteComment(View):
    """ Retrieves comment and deletes it """

    def get(self, request, comment_id):
        try:
            comment = get_object_or_404(Comment, id=comment_id)
            post = comment.post
            slug = post.slug

            if request.user == comment.author:
                comment.delete()
                messages.success(request,
                                 "Your comment has been deleted!")
                return redirect(reverse("post_detail", kwargs={"slug": slug}))
            else:
                return HttpResponse(["POST"])

        except Exception as exception:
            raise type(exception)(str(exception)) from exception
