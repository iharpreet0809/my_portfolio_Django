"""
Django Models for Portfolio Application

This module contains all the database models for the portfolio website.

"""

from django.db import models
from django.contrib.auth.models import User
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