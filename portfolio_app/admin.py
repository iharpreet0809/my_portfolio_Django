from django.contrib import admin
from .models import Contact
from django import forms



class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

# Register models
admin.site.register(Contact, ContactAdmin)


admin.site.site_title = "Admin Panel" #on tab title
admin.site.site_header = "iharpreet Admin Panel" #on top of username and password dialog box
admin.site.index_title = "Welcome to the Admin Panel" #on the index page logo
