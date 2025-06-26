#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.

This script is Django's command-line utility for administrative tasks.
It allows you to run various Django management commands like:
- python manage.py runserver (start development server)
- python manage.py migrate (apply database migrations)
- python manage.py collectstatic (collect static files)
- python manage.py createsuperuser (create admin user)
- python manage.py shell (open Django shell)
"""

import os
import sys


def main():
    """
    Run administrative tasks.
    
    This function sets up the Django environment and executes
    the requested management command.
    """
    # Set the Django settings module for this project
    # This tells Django which settings file to use
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portfolio_django.settings")
    
    try:
        # Import Django's command-line execution function
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Handle the case where Django is not installed
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Execute the Django management command with the provided arguments
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    # Only run main() if this script is executed directly
    # (not imported as a module)
    main()
