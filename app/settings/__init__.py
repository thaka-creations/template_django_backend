import os

DJANGO_ENV = os.getenv("ENVIRONMENT", "local").lower()

if DJANGO_ENV == "production":
    from .production import *
else:
    from .local import *
