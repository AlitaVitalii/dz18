from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('blog/', views.BlogListView.as_view(), name='blogs'),
    path('blog/<int:pk>/', views.BlogDetailView.as_view(), name='blog-detail'),
    path('myblog/', views.MyBlogListView.as_view(), name='my-blog'),
    path('blog/create/', views.BlogCreate.as_view(), name='blog_create'),
    path('blog/update/<int:pk>/', views.BlogUpdate.as_view(), name='blog_update'),

    path('blog/<int:pk>/create/', views.CommentCreate.as_view(), name='comment_create'),

    path('user/', views.UserListView.as_view(), name='users'),
    path('user<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),


]
