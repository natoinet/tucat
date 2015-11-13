from django.db import models

from tucat.core.models import TimeStampedModel, STATUS_CHOICES

'''
class CeleryTaskLock(TimeStampedModel):
    package_name = models.CharField(max_length=200, unique=True)
    task_id = models.CharField(max_length=200)
'''

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


'''
class TucatTask(TimeStampedModel):
    name = models.CharField(max_length=200)
    task_id = models.CharField(max_length=200)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    total_nb = models.IntegerField(default=-1)
    current_nb = models.IntegerField(default=-0)
    currently = models.CharField(max_length=200, blank=True, null=True)
    lock = models.ForeignKey(CeleryTaskLock, blank=True, null=True)

    
    def is_current(self):
        b_current = False
        if (self.lock is not None):
            b_current = (task_id == lock.task_id)
        return b_current
    is_current.boolean = True
    is_current.short_description = 'Current?'

    def progress(self):
        return (self.current_nb / self.total_nb * 100)
    progress.short_description = 'Extraction %'

    def is_locked(self):
        return (self.lock != None)
'''
