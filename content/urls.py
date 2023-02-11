from django.urls import path
from content.views import LoadIndex, LoadMental


urlpatterns = [
    path('', LoadIndex, name='home'),
    path('mental/', LoadMental, name='mental'),
]