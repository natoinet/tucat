from django.db import models

from tucat.core.models import TimeStampedModel, STATUS_CHOICES

class TucatApplication(TimeStampedModel):
    name = models.CharField(max_length=200, default='')
    command_name = models.CharField(max_length=200, default='')
    package_name = models.CharField(max_length=200, unique=True, default='')
    task_id = models.CharField(max_length=200, default='')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='s')

    def update(self, task_id='', status='f'):
        self.task_id = task_id
        self.status = status
        self.save()

    def __str__(self):
        return self.name

    class Meta:
        abstract = False

class TucatElement(TimeStampedModel):
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    application = models.ForeignKey(TucatApplication)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        abstract = True

