from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime
from .forms import ContactForm, BlogSearchForm
from .models import Contact, BlogPost, Category, Author

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

# Blog Views
def blog_list(request):
    """Display list of published blog posts with filtering and search."""
    # Get all published posts
    posts = BlogPost.objects.filter(is_published=True).select_related('author', 'category')
    
    # Initialize search form
    search_form = BlogSearchForm(request.GET)
    
    if search_form.is_valid():
        # Search functionality
        query = search_form.cleaned_data.get('q')
        if query:
            posts = posts.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()
        
        # Category filter
        category = search_form.cleaned_data.get('category')
        if category:
            posts = posts.filter(category=category)
        
        # Tag filter
        tags_query = search_form.cleaned_data.get('tags')
        if tags_query:
            tag_names = [tag.strip() for tag in tags_query.split(',') if tag.strip()]
            posts = posts.filter(tags__name__in=tag_names).distinct()
        
        # Date range filter
        date_from = search_form.cleaned_data.get('date_from')
        date_to = search_form.cleaned_data.get('date_to')
        
        if date_from:
            posts = posts.filter(published_date__date__gte=date_from)
        if date_to:
            posts = posts.filter(published_date__date__lte=date_to)
        
        # Featured posts filter
        featured_only = search_form.cleaned_data.get('featured_only')
        if featured_only:
            posts = posts.filter(featured=True)
    
    # Get categories and tags for sidebar
    categories = Category.objects.all()
    all_tags = BlogPost.tags.all()
    
    # Pagination
    paginator = Paginator(posts, 6)  # Show 6 posts per page
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'posts': posts,
        'search_form': search_form,
        'categories': categories,
        'all_tags': all_tags,
        'featured_posts': BlogPost.objects.filter(is_published=True, featured=True)[:3],
    }
    
    return render(request, 'blog/blog_list.html', context)

def blog_detail(request, slug):
    """Display individual blog post detail."""
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Increment view count
    post.increment_views()
    
    # Get related posts
    related_posts = BlogPost.objects.filter(
        is_published=True,
        category=post.category
    ).exclude(id=post.id)[:3]
    
    # Get recent posts
    recent_posts = BlogPost.objects.filter(is_published=True).exclude(id=post.id)[:5]
    
    context = {
        'post': post,
        'related_posts': related_posts,
        'recent_posts': recent_posts,
    }
    
    return render(request, 'blog/blog_detail.html', context)

def blog_category(request, slug):
    """Display posts filtered by category."""
    category = get_object_or_404(Category, slug=slug)
    posts = BlogPost.objects.filter(
        is_published=True,
        category=category
    ).select_related('author', 'category')
    
    # Pagination
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'posts': posts,
        'category': category,
        'categories': Category.objects.all(),
        'all_tags': BlogPost.tags.all(),
    }
    
    return render(request, 'blog/blog_category.html', context)

def blog_tag(request, tag_slug):
    """Display posts filtered by tag."""
    from taggit.models import Tag
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = BlogPost.objects.filter(
        is_published=True,
        tags__name__in=[tag.name]
    ).select_related('author', 'category')
    
    # Pagination
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'posts': posts,
        'tag': tag,
        'categories': Category.objects.all(),
        'all_tags': BlogPost.tags.all(),
    }
    
    return render(request, 'blog/blog_tag.html', context)

@require_http_methods(["GET"])
def blog_search_ajax(request):
    """AJAX endpoint for blog search."""
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    tags = request.GET.get('tags', '')
    
    posts = BlogPost.objects.filter(is_published=True).select_related('author', 'category')
    
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query)
        )
    
    if category_id:
        posts = posts.filter(category_id=category_id)
    
    if tags:
        tag_names = [tag.strip() for tag in tags.split(',') if tag.strip()]
        posts = posts.filter(tags__name__in=tag_names).distinct()
    
    # Limit results for AJAX
    posts = posts[:10]
    
    data = []
    for post in posts:
        data.append({
            'title': post.title,
            'excerpt': post.excerpt,
            'author': post.author.user.get_full_name() or post.author.user.username,
            'category': post.category.name,
            'published_date': post.published_date.strftime('%B %d, %Y') if post.published_date else '',
            'url': post.get_absolute_url(),
            'cover_image': post.cover_image.url if post.cover_image else '',
        })
    
    return JsonResponse({'posts': data})

def blog_rss_feed(request):
    """Generate RSS feed for blog posts."""
    from django.contrib.syndication.views import Feed
    from django.utils.feedgenerator import Rss201rev2Feed
    
    posts = BlogPost.objects.filter(is_published=True)[:20]
    
    # This is a simplified RSS feed - in production you might want to use Django's syndication framework
    context = {
        'posts': posts,
        'site_name': 'Harpreet Singh Portfolio',
        'site_url': request.build_absolute_uri('/'),
    }
    
    return render(request, 'blog/rss_feed.xml', context, content_type='application/xml')


