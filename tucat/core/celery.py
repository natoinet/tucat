from __future__ import absolute_import

import os
import time

from celery import Celery

from django.conf import settings

import environ

# Read .env file, in order to set DJANGO_SETTINGS_MODULE
root = environ.Path(__file__) - 3
environ.Env().read_env(root() + '/.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tucat.config.settings')

app = Celery('tucat')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
