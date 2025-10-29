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
    It includes fields for name, email, subject, message, and CAPTCHA with
    Bootstrap styling for a modern look.
    """
    captcha = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Answer'
        }),
        label='CAPTCHA',
        help_text='Please solve the math problem above'
    )
    
    def __init__(self, *args, **kwargs):
        self.captcha_answer = kwargs.pop('captcha_answer', None)
        super().__init__(*args, **kwargs)
        if self.captcha_answer:
            self.fields['captcha'].help_text = f'solve: {self.captcha_answer[0]}'
    
    def clean_captcha(self):
        captcha = self.cleaned_data.get('captcha')
        if not captcha:
            raise forms.ValidationError("Please enter the CAPTCHA answer.")
        
        if self.captcha_answer and str(captcha).strip() != str(self.captcha_answer[1]):
            raise forms.ValidationError("Incorrect CAPTCHA answer. Please try again.")
        
        return captcha

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
