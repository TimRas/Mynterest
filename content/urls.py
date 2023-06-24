from django.urls import path
from . import views

urlpatterns = [
    path('', views.TopicList.as_view(), name='home'),
    path('posts/<str:topic>/', views.PostList.as_view(), name='posts'),
    path('check_can_post/<str:topic>', views.AuthCheckPost.as_view(),
         name='check_can_post'),
    path('post_detail/<slug:slug>/', views.PostDetail.as_view(),
         name='post_detail'),
    path('check_like_post/<slug:slug>', views.AuthCheckLike.as_view(),
         name='check_like_post'),
    path('create_post/<slug:topic>/', views.CreatePost.as_view(),
         name='create_post'),
    path('edit_post/<slug:slug>/', views.EditPost.as_view(), name='edit_post'),
    path('edit_comment/<int:comment_id>/', views.EditComment.as_view(),
         name='edit_comment'),
    path('delete_post/<slug:slug>/', views.DeletePost.as_view(),
         name='delete_post'),
    path('delete_comment/<int:comment_id>/', views.DeleteComment.as_view(),
         name='delete_comment'),
    path('like/<slug:slug>/', views.PostLike.as_view(), name='post_like'),
]
