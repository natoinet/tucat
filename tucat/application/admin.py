import logging

from django.contrib import admin
from django.core.management import call_command

# Register your models here.
from djcelery.models import (TaskState, WorkerState,
                 PeriodicTask, IntervalSchedule, CrontabSchedule)

from tucat.application.models import TucatApplication
#from tucat.twitter_extraction.models import TwitterListExtraction, Manager, TwitterApp, TwitterUser, CustomTaskState, TwitterApiConstant, TwitterApiStatusCode

#admin.site.unregister(TaskState)
#admin.site.unregister(WorkerState)
#admin.site.unregister(PeriodicTask)
#admin.site.unregister(IntervalSchedule)
#admin.site.unregister(CrontabSchedule)

logger = logging.getLogger('application')

def run(modeladmin, request, queryset):
    logger.info('Command run %s %s', request, queryset)

    for obj in queryset:
        logger.debug('Command run %s', obj)
        call_command(obj.command_name, obj=obj, run='run')
run.short_description = "Run the app"


def stop(modeladmin, request, queryset):
    logger.info('Command stop %s %s', request, queryset)

    for obj in queryset:
        logger.debug('Command stop %s', obj)
        call_command(obj.command_name, obj=obj, stop='stop')
stop.short_description = "Stop the app"

def unlock(modeladmin, request, queryset):
    logger.info('Command run %s %s', request, queryset)

    for obj in queryset:
        logger.debug('Command unlock %s', obj)
        call_command(obj.command_name, obj=obj, unlock='unlock')
unlock.short_description = "Unlock the app"

class TucatApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'modified', 'task_id')
    readonly_fields = ('modified', 'task_id', 'status')
    actions = [run, stop, unlock]


admin.site.register(TucatApplication, TucatApplicationAdmin)
