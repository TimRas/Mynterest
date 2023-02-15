from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views import View, generic
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Topic, Post, Comment
from .forms import CommentForm, PostForm


class TopicList(generic.ListView):
    model = Topic
    queryset = Topic.objects.all()
    template_name = "index.html"



# class PostList(generic.ListView):
#     model = Post
#     template_name = "posts.html"
#     paginate_by = 6

#     def get_queryset(self):
#         topic = self.kwargs['topic'] 
#         return Post.objects.filter(topic__slug=topic)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["post_form"] = PostForm()
#         context["slug"] = self.kwargs["slug"]
#         return context

#     def post(self, request, topic, **kwargs):

#         topic = self.kwargs['topic'] 
#         post_form = PostForm(data=request.POST)

#         if post_form.is_valid():
#             post_form.instance.email = request.user.email
#             post_form.instance.name = request.user.username
#             post = post_form.save(commit=False)
#             post.post = post
#             post.author = request.user
#             post.save()
#             messages.success(request, 'Your comment was successfully submitted!')
#             return redirect('post_detail', topic=topic)
#         else:
#             post_form = PostForm()

#         context = {
#             "post": post,
#             "post_form": post_form,
#         }

#         return render(request, "posts.html", context)

class PostList(View):

    def get(self, request, topic, *args, **kwargs):
        queryset = Post.objects.all()
        posts = queryset.filter(topic__slug=topic)
        post_form = PostForm()

        return render(
            request,
            "posts.html",
            {
                "posts": posts,
                'posted': False,
                "post_form": post_form,
                
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
            'posted': True,
            "posts": posts,

        },
    )


    
class PostDetail(View):

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
                'commented': False,
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


class PostLike(View):
    
    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))