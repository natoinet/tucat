from django.utils import timezone
from django.db import models
from django.db.models import signals
from django.core.files import File

#from private_storage.fields import PrivateFileField

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
    def create_collection(self, owner_name, list_name, completed, collection_name):
        collection = self.create(owner_name=owner_name, list_name=list_name, completed=completed, collection_name=collection_name)
        return collection


class ExtractionCollection(models.Model):
    owner_name = models.CharField(max_length=200)
    list_name = models.CharField(max_length=200)
    date = models.DateField(max_length=200, default=timezone.now)
    nb_users = models.IntegerField(default=0)
    completed = models.DateTimeField()
    collection_name = models.CharField(max_length=200, default='')

    objects = ExtractionCollectionManager()

    def __str__(self):
        return self.collection_name


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
    collection = models.ForeignKey(ExtractionCollection, on_delete=models.CASCADE)
    export_type = models.ForeignKey(ExportationType, on_delete=models.CASCADE)
    export_format = models.ForeignKey(ExportationFormat, on_delete=models.CASCADE)
    last_tweet = models.DateField(blank=True, null=True)
    link_file = models.CharField(blank=True, null=True, max_length=200)
    #file = PrivateFileField("File", default="")
    file = models.FileField(upload_to='output/', default=None)

    def update(self, task_id, status, link_file=None):
        self.task_id = task_id
        self.status = status

        if link_file is None:
            self.save()
        else:
            with open('./tucat/output/' + link_file, 'r') as f:
                self.file = File(f)
                self.save()

    class Meta:
        abstract = False
