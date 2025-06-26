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
    
]
