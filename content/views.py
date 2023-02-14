from django.shortcuts import render, get_object_or_404, reverse
from django.views import View, generic
from django.http import HttpResponseRedirect
from .models import Topic, Post, Comment
from .forms import CommentForm


# def LoadIndex(request):

    # topic_items = Topic.objects.all()
    # context = {
    #     'topic_items': topic_items 
    # }

#     return render(request, 'index.html')


# def LoadHealth(request):
#     return render(request, 'health.html')


# def LoadMental(request):

#     post_items = Post.objects.all()
#     context = {
#         'post_items': post_items 
#     }

#     return render(request, 'mental.html', context)


class TopicList(generic.ListView):
    model = Topic
    queryset = Topic.objects.all()
    template_name = "index.html"
    paginate_by = 4


class PostList(generic.ListView):
    model = Post
    queryset = Post.objects.all()
    template_name = "posts.html"
    paginate_by = 6

    def get_queryset(self):
        topic = self.kwargs['topic'] 
        return Post.objects.filter(topic__slug=topic)


# class Postlist(View):

#     def get(self, request, slug, *args, **kwargs):
#         queryset = Post.objects.filter()
#         posts = get_object_or_404(queryset, topic=topic)
#         comments = post.comments.all().order_by("-created_date")
#         liked = False
#         if post.likes.filter(id=self.request.user.id).exists():
#             liked = True

#         return render(
#             request,
#             "posts.html",
#             {
#                 "post": post,
#                 "comments": comments,
#                 "liked": liked
#             },
#         )



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
        queryset = Post.objects.all()
        post = get_object_or_404(queryset, slug=slug)
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