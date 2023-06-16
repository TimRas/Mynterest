from django.contrib import admin
from django.urls import path, include
from .views import handler404


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include("content.urls"), name="home"),
    path('summernote/', include('django_summernote.urls')),
]
handler404 = 'mynterest.views.handler404'
