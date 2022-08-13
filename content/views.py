from django.shortcuts import render
from django.views import generic
from .models import Topic


def LoadIndex(request):
    topic_items = Topic.objects.all()
    context = {
        'topic_items': topic_items 
    }

    # model = Topic
    # template_name = 'index.html'
    # paginate_by = 4
    return render(request, 'content/index.html', context)

def LoadHealth(request):
    return render(request, 'content/health.html')



