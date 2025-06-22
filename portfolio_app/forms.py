"""
Django Forms for Portfolio Application

This module contains all the form classes used throughout the application.
Forms handle user input validation and provide a clean interface for data collection.
"""

from django import forms
from .models import Contact, BlogPost, Category, Author
from django.contrib.auth.models import User
from taggit.forms import TagWidget

class ContactForm(forms.ModelForm):
    """
    Contact Form for Portfolio Homepage
    
    This form handles contact form submissions from visitors.
    It includes fields for name, email, subject, and message with
    Bootstrap styling for a modern look.
    """
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Your Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Your Email'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Message', 
                'rows': 5
            }),
        }

class BlogPostForm(forms.ModelForm):
    """
    Blog Post Creation/Editing Form
    
    This form is used in the admin interface for creating and editing blog posts.
    It includes all necessary fields for a complete blog post including
    SEO fields, publication status, and content management.
    """
    class Meta:
        model = BlogPost
        fields = [
            'title', 'content', 'excerpt', 'cover_image', 'category', 
            'tags', 'is_published', 'meta_title', 'meta_description', 'featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter blog title'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Brief summary of the post'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tags': TagWidget(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter tags separated by commas'
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'SEO title (max 60 characters)'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'SEO description (max 160 characters)'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

class BlogSearchForm(forms.Form):
    """
    Blog Search and Filter Form
    
    This form provides comprehensive search and filtering capabilities
    for the blog listing page. It includes text search, category filtering,
    tag filtering, date range filtering, and featured posts filtering.
    """
    # Text search field
    q = forms.CharField(
        required=False,  # Optional field
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search blogs...',
            'aria-label': 'Search'
        })
    )
    
    # Category dropdown filter
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,  # Optional field
        empty_label="All Categories",  # Default option
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    # Tag filter (comma-separated input)
    tags = forms.CharField(
        required=False,  # Optional field
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by tags...'
        })
    )
    
    # Date range filtering - start date
    date_from = forms.DateField(
        required=False,  # Optional field
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'  # HTML5 date picker
        })
    )
    
    # Date range filtering - end date
    date_to = forms.DateField(
        required=False,  # Optional field
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'  # HTML5 date picker
        })
    )
    
    # Featured posts only filter
    featured_only = forms.BooleanField(
        required=False,  # Optional field
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

class AuthorForm(forms.ModelForm):
    """
    Author Profile Form
    
    This form is used for creating and editing author profiles.
    It includes fields for bio, profile picture, and social media links.
    """
    class Meta:
        model = Author
        fields = ['bio', 'profile_picture', 'website', 'twitter', 'linkedin', 'github']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Tell us about yourself...'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control', 
                'placeholder': 'https://yourwebsite.com'
            }),
            'twitter': forms.URLInput(attrs={
                'class': 'form-control', 
                'placeholder': 'https://twitter.com/username'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'form-control', 
                'placeholder': 'https://linkedin.com/in/username'
            }),
            'github': forms.URLInput(attrs={
                'class': 'form-control', 
                'placeholder': 'https://github.com/username'
            }),
        } 