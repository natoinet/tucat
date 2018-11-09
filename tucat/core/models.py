# core/models.py

import logging
from hashlib import md5

from django.db import models

STATUS_CHOICES = (
    ('p', 'Pending'),
    ('r', 'Running'),
    ('c', 'Complete'),
    ('s', 'Stopped'),
    ('f', 'Failed'),
)

logger = logging.getLogger('core')

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides
    self-updating ``created`` and ``modified`` fields.
    """

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class DjangoAdminCeleryTaskLock(TimeStampedModel):
    '''
    Lock tasks managed by Django administration only
    '''
    task_id = models.CharField(max_length=200)
    md5_hex = models.CharField(max_length=32, unique=True)

    @staticmethod
    def hash(*args):
        logger.info('DjangoAdminCeleryTaskLock hashing %s', args)
        args_enc = str(args).encode('utf-8')
        return md5(args_enc).hexdigest()

    class Meta:
        abstract = False

class TucatTask(models.Model):
    name = models.CharField(max_length=200, default='')
    task_id = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='p')

    def update(self, task_id, status):
        self.task_id = task_id
        self.status = status
        self.save()

    def __str__(self):
        return self.name

    class Meta:
        abstract = True

class TwitterList(TimeStampedModel):
    """
    An abstract base class model that provides:
    - self-updating ``created`` and ``modified`` fields
    - list owner name and slug
    """

    list_owner = models.CharField(max_length=200)
    list_name = models.CharField(max_length=200)
    list_label = models.CharField(max_length=200, null=True, blank=True)
    is_enabled = models.BooleanField()
    status = models.CharField(max_length=1, default='p', editable=False)

    class Meta:
        abstract = True
