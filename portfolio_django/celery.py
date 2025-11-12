"""
Celery configuration for portfolio_django project.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_django.settings')

app = Celery('portfolio_django')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure Celery to work properly with Django
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    return f'Debug task completed: {self.request!r}'


