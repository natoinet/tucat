import logging
import re

from django.contrib import admin
from django.core.management import call_command
from django.http import HttpResponse
from django.utils.html import format_html
from django.shortcuts import redirect

from tucat.twitter_extraction.models import TwitterListExtraction, TwitterListExtractionExport, ExportationType, ExportationFormat, ExtractionCollection

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

#def download(self, request, queryset):
def download(modeladmin, request, queryset):
    for obj in queryset:
        logger.info('Command export download for %s', obj.link_file)
        #link_file = re.findall(r"\S+", obj.link_file)[1]
        f = open('./tucat/output/' + obj.link_file, 'r')
        #f = open(obj.file.url, 'r')
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = ('attachment; filename='+ obj.link_file)
        return response
download.short_description = "Download This export (only one at a time)"


class TwitterListExtractionAdmin(admin.ModelAdmin):
    list_display = ('owner_name', 'list_name', 'status', 'modified', 'is_enabled')
    readonly_fields = ('modified', 'status')

class TwitterListExtractionExportAdmin(admin.ModelAdmin):
    readonly_fields = ('task_id', 'status', 'link_file',)
    list_display = ('name', 'collection', 'export_type', 'export_format', 'last_tweet', 'task_id', 'status')#'file')#, 'get_file_url')#), 'download')
    actions = [run, stop, download]


    #def download(self, obj):
        #return format_html("<a href='/static/output/{0}'>{0}</a>", obj.link_file)
        #f = open('./tucat/output/' + obj.link_file, 'r')
        #response = HttpResponse(f, content_type='text/csv')
        #response['Content-Disposition'] = ('attachment; filename='+ obj.link_file)
        #return response
        #if obj.file is not "":
        #return format_html("<a href=" + redirect("/static/output/" + obj.link_file).url + ">{0}</a>", obj.link_file)
        #return format_html("<a href=" + obj.file.url + ">{0}</a>", obj.link_file)
        #else:
        #    return None
        #f = open('./tucat/output/' + obj.link_file, 'r')
        #response = HttpResponse(f, content_type='text/csv')
        #response['Content-Disposition'] = ('attachment; filename='+ obj.link_file)
        #return redirect(response)
        #return format_html("<a href=" + redirect(obj.file.url).url + ">{0}</a>", obj.file)


    #download.allow_tags = True
    #download.short_description = 'Download'

class ExtractionCollectionAdmin(admin.ModelAdmin):
    list_display = ('owner_name', 'list_name', 'completed')


admin.site.register(TwitterListExtraction, TwitterListExtractionAdmin)
admin.site.register(TwitterListExtractionExport, TwitterListExtractionExportAdmin)
admin.site.register(ExportationFormat)
admin.site.register(ExportationType)
admin.site.register(ExtractionCollection, ExtractionCollectionAdmin)
