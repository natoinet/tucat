import logging

from django.contrib import admin
from django.core.management import call_command

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


class TwitterListExtractionAdmin(admin.ModelAdmin):
    list_display = ('owner_name', 'list_name', 'status', 'modified', 'is_enabled')
    readonly_fields = ('modified', 'status')

class TwitterListExtractionExportAdmin(admin.ModelAdmin):
    readonly_fields = ('task_id', 'status', 'link_file',)
    list_display = ('name', 'collection', 'export_type', 'export_format', 'last_tweet', 'task_id', 'status', 'link_file')
    actions = [run, stop]

class ExtractionCollectionAdmin(admin.ModelAdmin):
    list_display = ('date', 'nb_users', 'completed')


admin.site.register(TwitterListExtraction, TwitterListExtractionAdmin)
admin.site.register(TwitterListExtractionExport, TwitterListExtractionExportAdmin)
admin.site.register(ExportationFormat)
admin.site.register(ExportationType)
admin.site.register(ExtractionCollection, ExtractionCollectionAdmin)

'''
def run(modeladmin, request, queryset):
    queryset.update(status='r')
    for obj in queryset:
        obj.run()
run.short_description = "Run the app"

def stop(modeladmin, request, queryset):
    queryset.update(status='s')
    for obj in queryset:
        obj.stop()
stop.short_description = "Stop the app"

class TucatTaskAdmin(admin.ModelAdmin):
    list_display = ('created', 'modified', 'name', 'status', 
        'is_current', 'extraction_progress', 'extraction_progress', 'currently')
    readonly_fields = ('created', 'modified', 'name', 'task_id', 
        'status', 'total_nb', 'current_nb', 'currently', 'lock')

class TucatApplicationAdmin(admin.ModelAdmin):
    list_display = ('modified', 'name', 'status', 'task_id', 'lock')
    readonly_fields = ('modified', 'task_id', 'status', 'lock')
    actions = [run, stop]
'''

'''
admin.site.register(TucatElement, TucatElementAdmin)
admin.site.register(TucatTask, TucatTaskAdmin)
admin.site.register(TucatApplication, TucatApplicationAdmin)
'''

'''
class TwitterListExtractionAdmin(admin.ModelAdmin):
    list_display = ('list_owner', 'list_name', 'list_label', 'status', 
        'modified', 'is_enabled', 'task_id', 'created')
    list_filter = ['list_owner', 'list_label', 'is_enabled']
    search_fields = ['list_owner', 'list_name']

class ExtractionsManagerAdmin(admin.ModelAdmin):
    list_display = ('cron', 'app_status')

class TwitterUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'is_enabled')

class TwitterAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'key')

class TwitterApiConstantAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'is_enabled')

class TwitterApiStatusCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'action', 'is_enabled')

admin.site.register(TwitterListExtraction, TwitterListExtractionAdmin)
admin.site.register(Manager, ExtractionsManagerAdmin)
admin.site.register(TwitterUser, TwitterUserAdmin)
admin.site.register(TwitterApp, TwitterAppAdmin)
admin.site.register(TwitterApiConstant, TwitterApiConstantAdmin)
admin.site.register(TwitterApiStatusCode, TwitterApiStatusCodeAdmin)
'''