"""
Django Forms for Portfolio Application

This module contains all the form classes used throughout the application.
Forms handle user input validation and provide a clean interface for data collection.
"""

from django import forms
from .models import Contact
from django.contrib.auth.models import User
import re

class ContactForm(forms.ModelForm):
    """
    Contact Form for Portfolio Homepage
    
    This form handles contact form submissions from visitors.
    It includes fields for name, email, subject, and message with
    Bootstrap styling for a modern look.
    """
    def clean_email(self):
        email = self.cleaned_data['email']
        # Only allow .com, .in, .org domains
        if not re.search(r'@[^@]+\.(com|in|org)$', email, re.IGNORECASE):
            raise forms.ValidationError("Only .com, .in, .org email addresses are allowed.")
        return email

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
