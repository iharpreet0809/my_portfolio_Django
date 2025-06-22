"""
Django Models for Portfolio Application

This module contains all the database models for the portfolio website.
Models include Contact form submissions, Blog categories, Authors, and Blog posts.
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from taggit.managers import TaggableManager
from django.utils import timezone

# Create your models here.

class Contact(models.Model):
    """
    Contact Form Model
    
    Stores contact form submissions from visitors.
    Used for the main contact form on the portfolio homepage.
    """
    name = models.CharField(max_length=100)  # Visitor's full name
    email = models.EmailField()  # Visitor's email address
    subject = models.CharField(max_length=200)  # Subject line of the message
    message = models.TextField()  # The actual message content
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when message was sent

    def __str__(self):
        """String representation for admin interface"""
        return f"{self.name} - {self.subject}"

    class Meta:
        verbose_name = "Contact Form Submission"
        verbose_name_plural = "Contact Form Submissions"

class Category(models.Model):
    """
    Blog Category Model
    
    Organizes blog posts into categories for better content organization.
    Each category has a name, slug (URL-friendly version), and description.
    """
    name = models.CharField(max_length=100, unique=True)  # Category name (e.g., "Technology", "Tutorials")
    slug = models.SlugField(max_length=100, unique=True, blank=True)  # URL-friendly version of name
    description = models.TextField(blank=True)  # Optional description of the category
    created_at = models.DateTimeField(auto_now_add=True)  # When category was created
    updated_at = models.DateTimeField(auto_now=True)  # When category was last updated

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided"""
        if not self.slug:
            self.slug = slugify(self.name)  # Convert "Web Development" to "web-development"
        super().save(*args, **kwargs)

    def __str__(self):
        """String representation for admin interface"""
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']  # Sort categories alphabetically

class Author(models.Model):
    """
    Author Model
    
    Extends Django's User model to store additional author information.
    Links to blog posts and contains social media profiles.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to Django User model
    bio = models.TextField(blank=True)  # Author's biography
    profile_picture = models.ImageField(upload_to='authors/', blank=True, null=True)  # Author's profile photo
    website = models.URLField(blank=True)  # Personal website URL
    twitter = models.URLField(blank=True)  # Twitter profile URL
    linkedin = models.URLField(blank=True)  # LinkedIn profile URL
    github = models.URLField(blank=True)  # GitHub profile URL
    created_at = models.DateTimeField(auto_now_add=True)  # When author profile was created
    updated_at = models.DateTimeField(auto_now=True)  # When author profile was last updated

    def __str__(self):
        """String representation - use full name if available, otherwise username"""
        return self.user.get_full_name() or self.user.username

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"

class BlogPost(models.Model):
    """
    Blog Post Model
    
    The main content model for blog posts. Includes rich text content,
    SEO fields, engagement tracking, and relationships to categories and authors.
    """
    # Status choices for post publication
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    # Basic post information
    title = models.CharField(max_length=200)  # Post title
    slug = models.SlugField(max_length=200, unique=True, blank=True)  # URL-friendly title
    content = RichTextField(config_name='blog')  # Rich text content using CKEditor
    excerpt = models.TextField(max_length=500, blank=True, help_text="Brief summary of the post")  # Short description
    cover_image = models.ImageField(upload_to='blog_covers/', blank=True, null=True)  # Featured image
    
    # Relationships to other models
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='blog_posts')  # Post author
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='blog_posts')  # Post category
    tags = TaggableManager(blank=True)  # Flexible tagging system
    
    # Publication status and timing
    is_published = models.BooleanField(default=False)  # Whether post is live
    published_date = models.DateTimeField(blank=True, null=True)  # When post was published
    created_at = models.DateTimeField(auto_now_add=True)  # When post was created
    updated_at = models.DateTimeField(auto_now=True)  # When post was last updated
    
    # SEO (Search Engine Optimization) fields
    meta_title = models.CharField(max_length=60, blank=True, help_text="SEO title (max 60 characters)")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO description (max 160 characters)")
    
    # Engagement and visibility fields
    views = models.PositiveIntegerField(default=0)  # Number of times post was viewed
    featured = models.BooleanField(default=False)  # Whether post is featured/promoted

    def save(self, *args, **kwargs):
        """Custom save method to auto-generate slug and set published date"""
        # Generate slug from title if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Set published_date when post is first published
        if self.is_published and not self.published_date:
            self.published_date = timezone.now()
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Return the URL for this post (used in admin and templates)"""
        return reverse('blog_detail', kwargs={'slug': self.slug})

    def __str__(self):
        """String representation for admin interface"""
        return self.title

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ['-published_date', '-created_at']  # Most recent first

    @property
    def reading_time(self):
        """
        Estimate reading time based on content length
        
        Returns:
            int: Estimated reading time in minutes (minimum 1 minute)
        """
        words_per_minute = 200  # Average reading speed
        word_count = len(self.content.split())
        minutes = word_count // words_per_minute
        return max(1, minutes)  # Ensure minimum 1 minute reading time

    def increment_views(self):
        """Increment the view count for this post"""
        self.views += 1
        self.save(update_fields=['views'])  # Only update the views field for efficiency
