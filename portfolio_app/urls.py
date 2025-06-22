"""
URL Configuration for Portfolio Application

This module defines the URL patterns for the portfolio application.
Each URL pattern maps to a specific view function that handles the request.
"""

from django.urls import path
from . import views

# URL patterns for the portfolio application
urlpatterns = [
    # Homepage with contact form
    path('', views.contact, name='contact'),
    
    # Blog URLs - Main blog functionality
    path('blogs/', views.blog_list, name='blog_list'),  # Blog listing page with search/filter
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),  # Individual blog post
    path('blogs/category/<slug:slug>/', views.blog_category, name='blog_category'),  # Posts by category
    path('blogs/tag/<slug:tag_slug>/', views.blog_tag, name='blog_tag'),  # Posts by tag
    path('blogs/search/ajax/', views.blog_search_ajax, name='blog_search_ajax'),  # AJAX search endpoint
    path('blogs/rss/', views.blog_rss_feed, name='blog_rss_feed'),  # RSS feed for blog posts
]
