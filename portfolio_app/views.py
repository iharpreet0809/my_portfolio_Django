from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

def contact(request):
    """Handle contact form submission and render the index page."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('/#contact-msg')
    else:
        form = ContactForm()
        # Clear any existing messages when the page is loaded normally
        storage = messages.get_messages(request)
        storage.used = True
    return render(request, 'index.html', {'form': form})


