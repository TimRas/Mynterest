from django.shortcuts import render
from django.views import generic
from .models import Topic


class TopicList(generic.ListView):
    model = Topic
    template_name = 'index.html'
    paginate_by = 4

