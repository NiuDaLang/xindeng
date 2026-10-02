from django.db import models

# Create your models here.
"""
The `core` app intentionally has no database models.
It exists to house cross-cutting utilities: image processing,
signals, and maintenance tasks.

Django still requires this module to exist for the app registry
to initialise correctly.
"""