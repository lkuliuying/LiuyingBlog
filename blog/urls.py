from django.urls import path
from . import views,api_views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('blog/detail/<int:blog_id>/', views.blog_detail, name='blog_detail'),

    path('blog/pub',views.pub_blog,name='pub_blog'),

    path('blog/comment',views.pub_comment,name='pub_comment'),

    path('search',views.search,name='search'),
    
    path('upload_editor/', views.upload_editor_file, name='upload_editor_file'),
    
    path('api/blogs/', api_views.api_blog_list, name='api_blog_list'),
    
    path('blog/<int:blog_id>/like/',views.toggle_like,name='toggle_like'),
    
    path('blog/<int:blog_id>/collect/', views.toggle_collection, name='toggle_collection'),
    
    path('comment/<int:comment_id>/like/', views.toggle_comment_like, name='toggle_comment_like'),
]