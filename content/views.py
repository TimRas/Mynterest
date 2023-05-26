from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views import View, generic
from django.http import HttpResponseRedirect
from django.utils.text import slugify
from .models import Topic, Post, Comment
from .forms import CommentForm, PostForm


class TopicList(generic.ListView):
    """ Displays a list of all topics """

    model = Topic
    queryset = Topic.objects.all()
    template_name = "index.html"


class PostList(View):
    """ Renders all all posts related to the given topic. Validates the submitted form, saves the new post in the database and redirects the user back to the post page with the given topic"""
    
    def get(self, request, topic, *args, **kwargs):
        queryset = Post.objects.all()
        topic = self.kwargs['topic'] 
        posts = queryset.filter(topic__slug=topic)
        post_form = PostForm()

        return render(
            request,
            "posts.html",
            {
                "posts": posts,
                "post_form": post_form,
                "topic": topic,              
            },
        )
    
    def post(self, request, topic, **kwargs):
        queryset = Post.objects.all()
        topic = self.kwargs['topic'] 
        posts = queryset.filter(topic__slug=topic)
        post_form = PostForm(data=request.POST)
          
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.slug = slugify(post.title)
            post.save()
        else:
            post_form = PostForm()

        return render(
            request,
            "posts.html",
        {   
            "post_form": post_form,
            "topic": topic,
            "posts": posts,

        },
    )

   
class PostDetail(View):
    """ Renders post retreived form database and renders comment form. Validates the submitted form, saves the comment and redirects user to the details page of given post"""
    
    def get(self, request, slug, *args, **kwargs):
        queryset = Post.objects.all()
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.all().order_by("-created_date")

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "comment_form": CommentForm()
            },
        )

    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        comments = post.comments.all().order_by("-created_date")
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
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


class CreatePost(View):
    """Render a post form in the given URL. Validate the submitted form, update the database, and redirect to the given topic page."""

    def get(self, request, topic, *args, **kwargs):
        topic_field = get_object_or_404(Topic, slug=topic)
        post_form = PostForm(initial={"topic": topic_field})  

        return render(request, "create_post.html", {"topic": topic_field, "post_form": post_form})

    def post(self, request):
        post_form = PostForm(request.POST)  # Instantiate the form with request.POST data

        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.slug = slugify(post.title)
            post.save()
            # Redirect to the respective page (replace "posts" and "topic" with the appropriate URL names and parameters)
            return redirect(reverse("posts", kwargs={"topic": topic}))
        else:
            # Form is not valid, handle the error condition
            return render(request, "create_post.html", {"form": post_form})



class EditPost(View):
    """ Render a form in the edit post html of the given post. Validates the submitted form, update in the database and redirects to the given topic page"""
    
    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        post_form = PostForm(instance=post)

        return render(request, "edit_post.html", {"post_form": post_form})

    def post(self, request, slug, *args, **kwargs):      
        post = get_object_or_404(Post, slug=slug)
        post_form = PostForm(request.POST, instance=post)

        if post_form.is_valid():
            post_form.instance.name = request.user.username
            post_form.save()
            post_form = PostForm()
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


class EditComment(View):
    """ Renders a form in the edit comment html of the given comment. validates the submitted form, update in the database and redirects to the post the comments belongs to"""

    def get(self, request, comment_id, *args, **kwargs):

        comment = get_object_or_404(Comment, id=comment_id)
        comment_form = CommentForm(instance=comment)

        return render(request, "edit_comment.html", {"comment_form": comment_form})

    def post(self, request, comment_id, *args, **kwargs):

        comment = get_object_or_404(Comment, id=comment_id)
        comment_form = CommentForm(request.POST, instance=comment)

        if comment_form.is_valid():
            comment_form.instance.name = request.user.username
            comment_form.save()
            comment_form = CommentForm()
        else:
            comment_form = CommentForm(request.POST, instance=comment)

        post = comment.post
        
        return redirect("post_detail", slug=post.slug)


class PostLike(View):
    """ The functionality for liking and unliking posts"""
    
    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)

        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))


class DeletePost(View):
    """ Retrieves post and deletes it """

    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        topic = post.topic.slug
        post.delete()

        return redirect(reverse("posts", kwargs={"topic": topic}))


class DeleteComment(View):
    """ Retrieves comment and deletes it """

    def get(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        post = comment.post
        slug = post.slug
        comment.delete()

        return redirect(reverse("post_detail", kwargs={"slug": slug}))

    