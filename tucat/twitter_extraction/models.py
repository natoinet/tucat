from django.db import models
from django.db.models import signals

from tucat.application.models import TucatElement
from tucat.core.models import TucatTask

#from tucat.core.models import TwitterList, TimeStampedModel, STATUS_CHOICES


class TwitterListExtraction(TucatElement):

    owner_name = models.CharField(max_length=200)
    list_name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.owner_name + ' > ' + self.list_name

    class Meta:
        abstract = False

class ExtractionCollectionManager(models.Manager):
    def create_collection(self, owner_name, list_name, nb_users, completed):
        collection = self.create(owner_name=owner_name, list_name=list_name, nb_users=nb_users, completed=completed)
        return collection

class ExtractionCollection(models.Model):
    owner_name = models.CharField(max_length=200)
    list_name = models.CharField(max_length=200)    
    nb_users = models.IntegerField()
    completed = models.DateTimeField()

    objects = ExtractionCollectionManager()

    def __str__(self):
        return self.owner_name + self.list_name + str(self.completed)


class ExportationType(models.Model):
    name = models.CharField(max_length=200)
    top_users = models.BooleanField()
    followers = models.BooleanField()
    friends = models.BooleanField()

    def __str__(self):
        return self.name

class ExportationFormat(models.Model):
    name = models.CharField(max_length=200)
    format = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class TwitterListExtractionExport(TucatTask):
    collection = models.ForeignKey(ExtractionCollection)
    export_type = models.ForeignKey(ExportationType)
    export_format = models.ForeignKey(ExportationFormat)
    last_tweet = models.DateField(blank=True, null=True)
    link_file = models.CharField(blank=True, null=True, max_length=200)

    class Meta:
        abstract = False


'''
def TwitterListExport_post_save(sender, instance, created, *args, **kwargs):
    """Argument explanation:

       sender - The model class. (MyModel)
       instance - The actual instance being saved.
       created - Boolean; True if a new record was created.

       *args, **kwargs - Capture the unneeded `raw` and `using`(1.3) arguments.
    """
    if (sender is TwitterListExport):
        print('blourp')
'''

'''
class CeleryTaskLock(TimeStampedModel):
    name = models.CharField(max_length=200, unique=True)
    task_id = models.CharField(max_length=200)
'''

'''
class TucatApplication(TimeStampedModel):
    name = models.CharField(max_length=200)
    task_id = models.CharField(max_length=200)
    lock = models.ForeignKey(CeleryTaskLock, blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
'''
'''
class TucatElement(TimeStampedModel):
    name = models.CharField(max_length=200)
    task_id = models.CharField(max_length=200)
    lock = models.ForeignKey(CeleryTaskLock, blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    application = models.ForeignKey(TucatApplication)
'''
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
'''
class Manager(models.Model):
    cron = models.ForeignKey(CrontabSchedule)
    manager_status = models.CharField(max_length=200, default='PENDING',  editable=False)
    task_id = models.CharField(max_length=200, default='', editable=False)

    def app_status(self):
        #return self.cron.schedule.app.tasks
        return self.cron.schedule.app.control.inspect().active()
        #app = Celery('proj')
        #return app.control.inspect().active()

    app_status.admin_order_field = 'Status'
    app_status.short_description = 'Running?'

class CustomTaskState(TimeStampedModel):
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

    def extraction_progress(self):
        return (self.current_nb / self.total_nb * 100)
    extraction_progress.short_description = 'Extraction %'

    def is_locked(self):
        return (self.lock != None)

class TwitterListExtraction(TwitterList):
    #Just to have something in the class otherwise it crashes
    class Meta:
        abstract = False

    app_label = "Twitter list extraction"

class TwitterApp(models.Model):
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=200)
    secret = models.CharField(max_length=200)

class TwitterUser(models.Model):
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=200)
    secret = models.CharField(max_length=200)
    is_enabled = models.BooleanField(default=True)

class TwitterApiConstant(models.Model):
    name = models.CharField(max_length=200)
    value = models.CharField(max_length=200)
    is_enabled = models.BooleanField(default=True)

class TwitterApiStatusCode(models.Model):
    code = models.IntegerField()
    action = models.CharField(max_length=10)
    is_enabled = models.BooleanField(default=True)
'''
