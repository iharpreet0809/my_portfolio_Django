"""
Django Views for Portfolio Application

This module contains all the view functions that handle HTTP requests and responses.
Views include contact form handling, blog listing, detail views, and search functionality.
"""

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

# Email imports for contact form functionality
from django.core.mail import EmailMessage, BadHeaderError
from smtplib import SMTPException
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ContactForm

def contact(request):
    """
    Handle contact form submission and render the index page.
    
    This view processes the contact form on the homepage. When a POST request
    is received, it validates the form data, saves it to the database, and
    sends an email notification to the site owner.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered index page with form or success message
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

# Blog Views

def blog_list(request):
    """
    Display list of published blog posts with filtering and search functionality.
    
    This view handles the main blog listing page. It supports:
    - Text search across title, content, excerpt, and tags
    - Category filtering
    - Tag filtering
    - Date range filtering
    - Featured posts filtering
    - Pagination (6 posts per page)
    
    Args:
        request: HTTP request object with optional GET parameters for filtering
        
    Returns:
        HttpResponse: Rendered blog list page with filtered posts
    """
    # Get all published posts with related author and category data
    posts = BlogPost.objects.filter(is_published=True).select_related('author', 'category')
    
    # Initialize search form with GET parameters
    search_form = BlogSearchForm(request.GET)
    
    if search_form.is_valid():
        # Handle text search
        query = search_form.cleaned_data.get('q')
        if query:
            # Search across multiple fields using Q objects for OR conditions
            posts = posts.filter(
                Q(title__icontains=query) |  # Search in title
                Q(content__icontains=query) |  # Search in content
                Q(excerpt__icontains=query) |  # Search in excerpt
                Q(tags__name__icontains=query)  # Search in tag names
            ).distinct()  # Remove duplicates from tag search
        
        # Handle category filtering
        category = search_form.cleaned_data.get('category')
        if category:
            posts = posts.filter(category=category)
        
        # Handle tag filtering (comma-separated tags)
        tags_query = search_form.cleaned_data.get('tags')
        if tags_query:
            # Split comma-separated tags and filter
            tag_names = [tag.strip() for tag in tags_query.split(',') if tag.strip()]
            posts = posts.filter(tags__name__in=tag_names).distinct()
        
        # Handle date range filtering
        date_from = search_form.cleaned_data.get('date_from')
        date_to = search_form.cleaned_data.get('date_to')
        
        if date_from:
            posts = posts.filter(published_date__date__gte=date_from)
        if date_to:
            posts = posts.filter(published_date__date__lte=date_to)
        
        # Handle featured posts filtering
        featured_only = search_form.cleaned_data.get('featured_only')
        if featured_only:
            posts = posts.filter(featured=True)
    
    # Get categories and tags for sidebar display
    categories = Category.objects.all()
    all_tags = BlogPost.tags.all()
    
    # Implement pagination (6 posts per page)
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        posts = paginator.page(paginator.num_pages)
    
    # Prepare context for template
    context = {
        'posts': posts,
        'search_form': search_form,
        'categories': categories,
        'all_tags': all_tags,
        'featured_posts': BlogPost.objects.filter(is_published=True, featured=True)[:3],  # Top 3 featured posts
    }
    
    return render(request, 'blog/blog_list.html', context)

def blog_detail(request, slug):
    """
    Display individual blog post detail page.
    
    This view shows a single blog post with its full content.
    It also increments the view count and provides related posts.
    
    Args:
        request: HTTP request object
        slug: URL slug of the blog post
        
    Returns:
        HttpResponse: Rendered blog detail page
    """
    # Get the specific blog post or return 404
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Increment view count for analytics
    post.increment_views()
    
    # Get related posts from the same category (excluding current post)
    related_posts = BlogPost.objects.filter(
        is_published=True,
        category=post.category
    ).exclude(id=post.id)[:3]  # Limit to 3 related posts
    
    # Get recent posts for sidebar (excluding current post)
    recent_posts = BlogPost.objects.filter(is_published=True).exclude(id=post.id)[:5]  # Limit to 5 recent posts
    
    context = {
        'post': post,
        'related_posts': related_posts,
        'recent_posts': recent_posts,
    }
    
    return render(request, 'blog/blog_detail.html', context)

def blog_category(request, slug):
    """
    Display posts filtered by category.
    
    Shows all published posts from a specific category with pagination.
    
    Args:
        request: HTTP request object
        slug: URL slug of the category
        
    Returns:
        HttpResponse: Rendered category page with filtered posts
    """
    # Get the category or return 404
    category = get_object_or_404(Category, slug=slug)
    
    # Get all published posts from this category
    posts = BlogPost.objects.filter(
        is_published=True,
        category=category
    ).select_related('author', 'category')
    
    # Implement pagination
    paginator = Paginator(posts, 6)  # 6 posts per page
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
        'categories': Category.objects.all(),  # For sidebar
        'all_tags': BlogPost.tags.all(),  # For sidebar
    }
    
    return render(request, 'blog/blog_category.html', context)

def blog_tag(request, tag_slug):
    """
    Display posts filtered by tag.
    
    Shows all published posts that have a specific tag with pagination.
    
    Args:
        request: HTTP request object
        tag_slug: URL slug of the tag
        
    Returns:
        HttpResponse: Rendered tag page with filtered posts
    """
    from taggit.models import Tag
    
    # Get the tag or return 404
    tag = get_object_or_404(Tag, slug=tag_slug)
    
    # Get all published posts with this tag
    posts = BlogPost.objects.filter(
        is_published=True,
        tags__name__in=[tag.name]
    ).select_related('author', 'category')
    
    # Implement pagination
    paginator = Paginator(posts, 6)  # 6 posts per page
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
        'categories': Category.objects.all(),  # For sidebar
        'all_tags': BlogPost.tags.all(),  # For sidebar
    }
    
    return render(request, 'blog/blog_tag.html', context)

@require_http_methods(["GET"])
def blog_search_ajax(request):
    """
    AJAX endpoint for blog search functionality.
    
    This view provides real-time search results via AJAX requests.
    It returns JSON data for dynamic search without page reload.
    
    Args:
        request: HTTP request object with GET parameters (q, category, tags)
        
    Returns:
        JsonResponse: JSON data containing search results
    """
    # Get search parameters from request
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    tags = request.GET.get('tags', '')
    
    # Start with all published posts
    posts = BlogPost.objects.filter(is_published=True).select_related('author', 'category')
    
    # Apply text search filter
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query)
        )
    
    # Apply category filter
    if category_id:
        posts = posts.filter(category_id=category_id)
    
    # Apply tag filter
    if tags:
        tag_names = [tag.strip() for tag in tags.split(',') if tag.strip()]
        posts = posts.filter(tags__name__in=tag_names).distinct()
    
    # Limit results for AJAX response (performance)
    posts = posts[:10]
    
    # Prepare JSON data
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
    """
    Generate RSS feed for blog posts.
    
    This view creates an RSS feed that can be consumed by RSS readers.
    It provides the latest 20 published posts in RSS format.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: XML RSS feed
    """
    from django.contrib.syndication.views import Feed
    from django.utils.feedgenerator import Rss201rev2Feed
    
    # Get latest 20 published posts
    posts = BlogPost.objects.filter(is_published=True)[:20]
    
    # Prepare context for RSS template
    context = {
        'posts': posts,
        'site_name': 'Harpreet Singh Portfolio',
        'site_url': request.build_absolute_uri('/'),
    }
    
    # Return XML response
    return render(request, 'blog/rss_feed.xml', context, content_type='application/xml')


