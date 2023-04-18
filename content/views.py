from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views import View, generic
from django.http import HttpResponseRedirect
from django.contrib import messages
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
        post = None
        post_form.instance.email = request.user.email
        post_form.instance.name = request.user.username
   
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.post = post
            post.author = request.user
            post.slug = post.title

            post.save()
            messages.success(request, 'Your comment was successfully submitted!')

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
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "liked": liked,
                "comment_form": CommentForm()
            },
        )

    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        comments = post.comments.all().order_by("-created_date")
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True
        
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            comment_form.instance.email = request.user.email
            comment_form.instance.name = request.user.username
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment was successfully submitted!')
        else:
            comment_form = CommentForm()
        
        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                'commented': True,
                "liked": liked,
                "comment_form": comment_form,
            },
        )


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
            posts = Post.objects.filter(topic__slug=post.topic.slug)
            post_form = PostForm()         
            return render(
                request,
                "posts.html",
                {
                    "posts": posts,
                    "post_form": post_form,
                    "topic": post.topic.slug,
                },
            )
        else:
            post_form = PostForm(request.POST, instance=post)
            messages.error(request, 'There was something wrong with your sumbission, please try again')
            return render(request, "edit_post.html", {"post_form": post_form})
        

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
            post = comment.post
            comment_form = CommentForm()
            return redirect("post_detail", slug=post.slug)
        else:
            comment_form = CommentForm(request.POST, instance=comment)
            messages.error(request, 'There was something wrong with your sumbission, please try again')
            return render(request, "edit_comment.html", {"comment_form": comment_form})


class PostLike(View):
    
    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))