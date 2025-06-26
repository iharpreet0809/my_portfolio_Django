"""
Django Views for Portfolio Application

This module contains all the view functions that handle HTTP requests and responses.

"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime
from .forms import ContactForm

# Email imports for contact form functionality
from django.core.mail import EmailMessage, BadHeaderError
from smtplib import SMTPException
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect

def contact(request):
    """
    Handle contact form submission and render the index page.
    
    This view processes the contact form on the homepage. When a POST request
    is received, it validates the form data, saves it to the database, and
    sends an email notification to the site owner.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered home page with form or success message
    """
    if request.method == 'POST':
        # Process form submission
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save form data to database
            form.save()

            # Extract form data for email
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Prepare email content
            full_message = f"""
New Query Submission on your website- "www.iharpreet.com":

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}
"""

            try:
                # Send email notification to site owner
                email_message = EmailMessage(
                    subject=f"{subject}-[Contact Form]",
                    body=full_message,
                    from_email='From Portfolio <talkwithharpreet@gmail.com>',
                    to=['talkwithharpreet@gmail.com'],
                    reply_to=[email],  # Allow direct reply to visitor
                )
                email_message.send(fail_silently=False)
                messages.success(request, 'Your message has been sent successfully!')
                return redirect('/#contact-msg')  # Redirect to contact section

            except (BadHeaderError, SMTPException):
                # Handle email sending errors
                return HttpResponse('There was an error sending the email.')
    else:
        # GET request - display empty form
        form = ContactForm()
        # Clear any existing messages when page loads normally
        storage = messages.get_messages(request)
        storage.used = True

    return render(request, 'index.html', {'form': form})
