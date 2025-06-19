from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

# def contact(request):
#     """Handle contact form submission and render the index page."""
#     if request.method == 'POST':
#         form = ContactForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Your message has been sent successfully!')
#             return redirect('/#contact-msg')
#     else:
#         form = ContactForm()
#         # Clear any existing messages when the page is loaded normally
#         storage = messages.get_messages(request)
#         storage.used = True
#     return render(request, 'index.html', {'form': form})


# views.py

from django.core.mail import EmailMessage, BadHeaderError
from smtplib import SMTPException
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ContactForm

def contact(request):
    """Handle contact form submission and render the index page."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save form to DB
            form.save()

            # Extract details
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Email content
            full_message = f"""
New Query Submission on your website- "www.iharpreet.com":

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}
"""

            try:
                email_message = EmailMessage(
                    subject=f"{subject}-[Contact Form]",
                    body=full_message,
                    from_email='From Portfolio <talkwithharpreet@gmail.com>',
                    to=['talkwithharpreet@gmail.com'],
                    reply_to=[email],
                )
                email_message.send(fail_silently=False)
                messages.success(request, 'Your message has been sent successfully!')
                return redirect('/#contact-msg')

            except (BadHeaderError, SMTPException):
                return HttpResponse('There was an error sending the email.')
    else:
        form = ContactForm()
        # Clear messages
        storage = messages.get_messages(request)
        storage.used = True

    return render(request, 'index.html', {'form': form})


