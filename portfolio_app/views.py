from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

def home(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('/#contact-section')
    else:
        form = ContactForm()
        # Clear any existing messages when the page is loaded normally
        storage = messages.get_messages(request)
        storage.used = True
    
    return render(request, 'index.html', {'form': form})
    from django.core.mail import send_mail
    from django.conf import settings

def home(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            
            # Send email
            name = form.cleaned_data['name']
            email = form.cleaned_data['email'] 
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            email_message = f"""
            New contact form submission:
            
            Name: {name}
            Email: {email}
            Subject: {subject}
            Message: {message}
            """
            
            try:
                send_mail(
                    subject=f'Contact Form: {subject}',
                    message=email_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
            except Exception as e:
                messages.error(request, 'Failed to send email. Your message was saved in our database.')
                return redirect('/#contact-section')
                
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('/#contact-section')
    else:
        form = ContactForm()
        # Clear any existing messages when the page is loaded normally
        storage = messages.get_messages(request)
        storage.used = True
    
    return render(request, 'index.html', {'form': form})

