from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import handler404


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')), 
    path('', include("content.urls"), name="home"),
    path('summernote/', include('django_summernote.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = 'mynterest.views.handler404'

