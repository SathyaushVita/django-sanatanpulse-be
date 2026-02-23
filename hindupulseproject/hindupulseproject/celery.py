# hindupulseproject/celery.py

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hindupulseproject.settings')

# Create the Celery app.
app = Celery('hindupulseproject')

# Load settings from Django settings.py with a CELERY_ prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover tasks from all registered Django app configs.
app.autodiscover_tasks()
