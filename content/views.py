from django.shortcuts import render, get_object_or_404
from django.views import View, generic
from .models import Topic, Post, Comment


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
    template_name = "mental.html"
    paginate_by = 6


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
                "liked": liked
            },
        )
