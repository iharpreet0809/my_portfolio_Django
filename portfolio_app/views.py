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
from django.views.decorators.csrf import csrf_exempt
import json

# Email imports for contact form functionality
from django.core.mail import EmailMessage, BadHeaderError
from smtplib import SMTPException
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.contrib.auth.views import LoginView
from django.conf import settings
import random

from django.core.mail import send_mail

from django.template.loader import render_to_string

from django.urls import reverse
from django.http import HttpResponseRedirect

import time

User = get_user_model()

def generate_captcha():
    """
    Generate a random math problem for CAPTCHA.
    Returns a tuple of (question, answer).
    Ensures all results are positive numbers under 100.
    """
    # Generate numbers between 1 and 50 to ensure sum is under 100
    num1 = random.randint(1, 50)
    num2 = random.randint(1, 50)
    
    # Only use addition
    answer = num1 + num2
    
    # Create the question string
    question = f"{num1} + {num2} = ?"
    
    return (question, answer)

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
        # Get the CAPTCHA answer from session
        captcha_answer = request.session.get('captcha_answer')
        
        # Process form submission
        form = ContactForm(request.POST, captcha_answer=captcha_answer)
        if form.is_valid():
            # Save form data to database
            form.save()

            # Extract form data for email
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Prepare email content body
            full_message = f"""
                            New Query-Contact Submission on your website- "www.iharpreet.com":

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
                    from_email='From Portfolio <talkwithharpreet@gmail.com>', #sender email yourself
                    to=['talkwithharpreet@gmail.com'],
                    reply_to=[email],  # Allow direct reply to visitor
                )
                email_message.send(fail_silently=False)
                
                # Clear the CAPTCHA from session after successful submission
                request.session.pop('captcha_answer', None)
                
                messages.success(request, 'Your message has been sent successfully!')
                return redirect('/#contact-msg')  # Redirect to contact section

            except (BadHeaderError, SMTPException):
                # Handle email sending errors
                return HttpResponse('There was an error sending the email.')
        else:
            # Form is invalid - generate new CAPTCHA and show errors
            captcha_question, captcha_answer = generate_captcha()
            request.session['captcha_answer'] = (captcha_question, captcha_answer)
            
            # Recreate form with new CAPTCHA
            form = ContactForm(request.POST, captcha_answer=(captcha_question, captcha_answer))
            
            # Add error message for CAPTCHA
            if 'captcha' in form.errors:
                messages.error(request, 'Incorrect CAPTCHA answer. Please try again.')
            
            return redirect('/#contact-msg')  # Redirect to contact section with errors
    else:
        # GET request - display empty form
        # Generate new CAPTCHA for fresh form
        captcha_question, captcha_answer = generate_captcha()
        request.session['captcha_answer'] = (captcha_question, captcha_answer)
        
        form = ContactForm(captcha_answer=(captcha_question, captcha_answer))
        # Clear any existing messages when page loads normally
        storage = messages.get_messages(request)
        storage.used = True

    return render(request, 'index.html', {'form': form})

def mask_email(email):
    try:
        username, domain = email.split('@')
        if len(username) <= 8:
            masked = username
        else:
            masked = username[:4] + '*' * (len(username)-8) + username[-4:]
        return masked + '@' + domain
    except Exception:
        return email


#admin login 2fa
def admin_login_2fa(request):
    """
    Custom admin login view with OTP two-factor authentication.
    Step 1: Validate username/password, generate/send OTP, show OTP field.
    Step 2: Validate OTP, log in user.
    Also supports resending OTP with a cooldown.
    """
    context = {'site_header': 'iharpreet Admin Panel'}
    OTP_COOLDOWN_SECONDS = 61  # 2 minutes
    now = int(time.time())
    if request.method == 'POST':
        step = request.POST.get('step', 'credentials')
        username = request.POST.get('username')
        password = request.POST.get('password')
        otp = request.POST.get('otp')
        resend = request.POST.get('resend')

        if step == 'credentials':
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_active and user.is_staff:
                # Generate OTP
                otp_code = str(random.randint(100000, 999999))
                request.session['otp_user_id'] = user.id
                request.session['otp_code'] = otp_code
                request.session['otp_valid'] = True
                request.session['otp_last_sent'] = now
                request.session['otp_email'] = user.email
                request.session['otp_stage'] = True  # Set OTP stage flag
                # Send OTP via email
                subject = 'Your Admin Panel OTP'
                message = f'Your OTP for admin login is: {otp_code}'
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                # Store username for GET
                request.session['otp_username'] = username
                # Store masked email for GET
                request.session['otp_masked_email'] = mask_email(user.email)
                # Redirect to avoid resending OTP on refresh
                return HttpResponseRedirect(request.path)
            else:
                context['error'] = 'Invalid username or password.'
                return render(request, 'admin/login.html', context)
        elif step == 'otp':
            if resend:
                # Resend OTP logic
                otp_failed = request.session.get('otp_failed', False)
                if not otp_failed:
                    last_sent = request.session.get('otp_last_sent', 0)
                    if now - last_sent < OTP_COOLDOWN_SECONDS:
                        wait_seconds = OTP_COOLDOWN_SECONDS - (now - last_sent)
                        context['otp_required'] = True
                        context['username'] = username
                        context['email'] = request.session.get('otp_email')
                        context['masked_email'] = request.session.get('otp_masked_email')
                        context['cooldown'] = wait_seconds
                        context['otp_sent'] = False
                        context['error'] = f'You Entered the wrong OTP. Please try to resend OTP'
                        return render(request, 'admin/login.html', context)
                # If otp_failed is True, allow immediate resend and reset the flag
                request.session['otp_failed'] = False
                # Generate and send new OTP
                user_id = request.session.get('otp_user_id')
                user = User.objects.get(id=user_id)
                otp_code = str(random.randint(100000, 999999))
                request.session['otp_code'] = otp_code
                request.session['otp_last_sent'] = now
                request.session['otp_valid'] = True
                request.session['otp_email'] = user.email
                subject = 'Your Admin Panel OTP'
                message = f'Your OTP for admin login is: {otp_code}'
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                context['otp_required'] = True
                context['otp_sent'] = True
                context['username'] = username
                context['email'] = user.email
                context['masked_email'] = mask_email(user.email)
                context['info'] = 'A new OTP has been sent to your email.'
                context['cooldown'] = OTP_COOLDOWN_SECONDS  # Always set cooldown after resending OTP
                return render(request, 'admin/login.html', context)
            # Normal OTP check
            if request.session.get('otp_valid') and request.session.get('otp_code') == otp:
                user_id = request.session.get('otp_user_id')
                user = User.objects.get(id=user_id)
                auth_login(request, user)
                # Clean up session
                request.session.pop('otp_code', None)
                request.session.pop('otp_user_id', None)
                request.session.pop('otp_valid', None)
                request.session.pop('otp_last_sent', None)
                request.session.pop('otp_email', None)
                request.session.pop('otp_failed', None)
                request.session.pop('otp_stage', None)
                request.session.pop('otp_username', None)
                return HttpResponseRedirect(reverse('admin:index'))
            else:
                context['otp_required'] = True
                context['username'] = username
                context['email'] = request.session.get('otp_email')
                context['masked_email'] = request.session.get('otp_masked_email')
                context['error'] = 'Invalid OTP. Please try again.'
                request.session['otp_failed'] = True  # Set flag for immediate resend
                return render(request, 'admin/login.html', context)
    else:
        # GET request
        if request.session.get('otp_stage'):
            context['otp_required'] = True
            context['username'] = request.session.get('otp_username')
            context['email'] = request.session.get('otp_email')
            context['masked_email'] = request.session.get('otp_masked_email')
            # Calculate cooldown
            last_sent = request.session.get('otp_last_sent', 0)
            seconds_left = OTP_COOLDOWN_SECONDS - (now - last_sent)
            if seconds_left > 0:
                context['cooldown'] = seconds_left
            return render(request, 'admin/login.html', context)
        return render(request, 'admin/login.html', context)

def admin_login_reset(request):
    # Clear all OTP-related session variables
    for key in [
        'otp_user_id', 'otp_code', 'otp_valid', 'otp_last_sent', 'otp_email',
        'otp_failed', 'otp_stage', 'otp_username', 'otp_masked_email']:
        request.session.pop(key, None)
    return redirect('admin_login_2fa')

@csrf_exempt
def refresh_captcha_ajax(request):
    """
    AJAX endpoint to refresh CAPTCHA without reloading the page.
    """
    if request.method == 'POST':
        # Generate new CAPTCHA
        captcha_question, captcha_answer = generate_captcha()
        request.session['captcha_answer'] = (captcha_question, captcha_answer)
        
        return JsonResponse({
            'question': captcha_question,
            'success': True
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
