from django.db import models

from tucat.application.models import TucatElement


class TwitterListStreaming(TucatElement):
    owner_name = models.CharField(max_length=200)
    list_name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.owner_name + ' > ' + self.list_name

    class Meta:
        abstract = False
