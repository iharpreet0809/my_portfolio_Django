from django.urls import path
from . import views

urlpatterns = [
    path('', views.contact, name='contact'),
    
    # Blog URLs
    path('blogs/', views.blog_list, name='blog_list'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('blogs/category/<slug:slug>/', views.blog_category, name='blog_category'),
    path('blogs/tag/<slug:tag_slug>/', views.blog_tag, name='blog_tag'),
    path('blogs/search/ajax/', views.blog_search_ajax, name='blog_search_ajax'),
    path('blogs/rss/', views.blog_rss_feed, name='blog_rss_feed'),
]
