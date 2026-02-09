import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sri_webie.settings")

app = Celery("sri_webie")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()