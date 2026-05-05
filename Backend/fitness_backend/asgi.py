"""
ASGI config for fitness_backend project.
Supports async views for non-blocking recommendation generation.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
application = get_asgi_application()
