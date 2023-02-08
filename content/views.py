from django.shortcuts import render
from django.views import generic
from .models import Topic


def LoadIndex(request):
    topic_items = Topic.objects.all()
    context = {
        'topic_items': topic_items 
    }

    model = Topic
    template_name = 'index.html'
    return render(request, 'index.html', context)

def LoadHealth(request):
    return render(request, 'health.html')



