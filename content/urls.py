from django.urls import path
from . import views

urlpatterns = [
    path('', views.TopicList.as_view(), name='home'),
    path('posts/<str:topic>/', views.PostList.as_view(), name='posts'),
    path('post_detail/<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
    path('edit_post/<slug:slug>/', views.EditPost.as_view(), name='edit_post'),
    path('edit_comment/<int:comment_id>/', views.EditComment.as_view(), name='edit_comment'),
    path('delete_post/<slug:slug>/', views.DeletePost.as_view(), name='delete_post'),
    path('like/<slug:slug>/', views.PostLike.as_view(), name='post_like'),
]
