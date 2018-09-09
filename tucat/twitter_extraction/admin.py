import logging
import re

from django.contrib import admin
from django.core.management import call_command
from django.http import HttpResponse

from tucat.twitter_extraction.models import TwitterListExtraction, TwitterListExtractionExport, ExportationType, ExportationFormat, ExtractionCollection
#from tucat.twitter_extraction.models import TwitterListExtraction, Manager, TwitterApp, TwitterUser, CustomTaskState, TwitterApiConstant, TwitterApiStatusCode

logger = logging.getLogger('application')

def run(modeladmin, request, queryset):
    logger.info('Command run %s %s', request, queryset)

    for obj in queryset:
        logger.debug('Command export run %s', obj)
        call_command('export', obj=obj, run='run')
run.short_description = "Run the export"

def stop(modeladmin, request, queryset):
    logger.info('Command run %s %s', request, queryset)

    for obj in queryset:
        logger.debug('Command export stop %s', obj)
        call_command('export', obj=obj, stop='stop')
stop.short_description = "Stop the export"

def download(self, request, queryset):
    for obj in queryset:
        logger.info('Command export download for %s', obj.link_file)
        link_file = re.findall(r"\S+", obj.link_file)[1]
        f = open('./tucat/output/' + link_file, 'r')
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = ('attachment; filename='+ link_file)
        return response
download.short_description = "Download the export."


class TwitterListExtractionAdmin(admin.ModelAdmin):
    list_display = ('owner_name', 'list_name', 'status', 'modified', 'is_enabled')
    readonly_fields = ('modified', 'status')

class TwitterListExtractionExportAdmin(admin.ModelAdmin):
    readonly_fields = ('task_id', 'status', 'link_file',)
    list_display = ('name', 'collection', 'export_type', 'export_format', 'last_tweet', 'task_id', 'status', 'link_file')
    actions = [run, stop, download]
    

class ExtractionCollectionAdmin(admin.ModelAdmin):
    #list_display = ('date', 'nb_users', 'completed')
    list_display = ('owner_name', 'list_name', 'completed')


admin.site.register(TwitterListExtraction, TwitterListExtractionAdmin)
admin.site.register(TwitterListExtractionExport, TwitterListExtractionExportAdmin)
admin.site.register(ExportationFormat)
admin.site.register(ExportationType)
admin.site.register(ExtractionCollection, ExtractionCollectionAdmin)
