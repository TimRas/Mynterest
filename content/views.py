from django.shortcuts import render
from .models import Topic, Post


def LoadIndex(request):

    # topic_items = Topic.objects.all()
    # context = {
    #     'topic_items': topic_items 
    # }

    return render(request, 'index.html')


def LoadHealth(request):
    return render(request, 'health.html')


def LoadMental(request):

    post_items = Post.objects.all()
    context = {
        'post_items': post_items 
    }

    return render(request, 'mental.html', context)
