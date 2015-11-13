from django.contrib import admin
from django.http import HttpResponseRedirect

# Register your models here.

from tucat.twitter_streaming.models import TwitterListStreaming

class TwitterListStreamingAdmin(admin.ModelAdmin):
    list_display = ('owner_name', 'list_name', 'status', 'modified', 'is_enabled')
    readonly_fields = ('modified', 'status')

admin.site.register(TwitterListStreaming, TwitterListStreamingAdmin)
