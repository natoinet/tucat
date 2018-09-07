from __future__ import absolute_import

import logging

import requests
from requests_oauthlib import OAuth1

from celery import task
from celery.app.task import Task
from pymongo import MongoClient
from django.conf import settings

from django_celery_beat.models import PeriodicTask

from tucat.core.token import get_app_token, get_users_token
from tucat.application.models import TucatApplication
from tucat.twitter_streaming.models import TwitterListStreaming

logger = logging.getLogger('twitter_streaming')


def do_streaming_cmd(action=None, obj=None):
    logger.info('do_cmd %s', action)

    #one_app = TucatApplication.objects.get(package_name=__package__)
    one_app = TucatApplication.objects.get(pk=obj.pk)
    periodic_streaming = PeriodicTask.objects.get(name=__package__)
    periodic_streaming.args = [obj.pk]
    periodic_streaming.save()

    if (action is 'run'):
        logger.info('Running')
        periodic_streaming.enabled = True
        periodic_streaming.save()
        one_app.update(status='r')
    elif (action is 'stop'):
        logger.info('Stopping')
        periodic_streaming.enabled = False
        periodic_streaming.save()
        one_app.update(status='s')
    else:
        logger.info('Unknown command')

@task
def do_run(obj_pk):
    try:
        logger.info('do_run streaming')

        #one_app = TucatApplication.objects.get(package_name=__package__)
        one_app = TucatApplication.objects.get(pk=obj_pk)
        tucat_elements = TwitterListStreaming.objects.filter(application_id=one_app.id, is_enabled=True)

        for element in tucat_elements:
            logger.info('do_run streaming %s %s', element.owner_name, element.list_name)
            tw_streaming(owner_name=element.owner_name, list_name=element.list_name)

        one_app.update(status='c')

        logger.info('do_run streaming success')
    except Exception as e:
        logger.error('do_run exception %s', e)
        one_app.update(status='f')
        periodictask = PeriodicTask.objects.get(name=__package__)
        periodictask.enabled = False
        periodictask.save()

    finally:
        logger.info('file:%s | finally', __file__)

def tw_streaming(owner_name='', list_name=''):
    logger.info('tw_streaming start %s %s', owner_name, list_name)
    
    app_token = get_app_token('twitter')
    users_token = get_users_token ('twitter')

    colname = owner_name + '-' + list_name
    #oauth = OAuth1(CONSUMER['key'], CONSUMER['secret'], TOKEN['key'], TOKEN['secret'], signature_type='auth_header')
    oauth = OAuth1(app_token['key'], app_token['secret'], users_token[0]['key'], users_token[0]['secret'], signature_type='auth_header')
    
    url = 'https://api.twitter.com/1.1/lists/statuses.json'
    parameters = {'owner_screen_name' : owner_name, 'slug' : list_name, 'include_rts' : '1'}

    since_id = get_since_id(colname)
    if (since_id > 0):
        logger.debug('since_id: %s', since_id)
        parameters['since_id'] = since_id
    else:
        parameters['count'] = '200'

    logger.info('url:%s | parameters:%s | auth:%s', url, parameters, str(oauth))

    request = requests.get(url=url, params=parameters, auth=oauth)

    _todb(colname, request)

def get_since_id(colname):
    db_name = __package__.replace('.', '_')
    logger.debug('filename:%s | db: %s', __file__, db_name)

    db = MongoClient(settings.MONGO_CLIENT)[db_name]

    if (db[colname].find().count() > 0):
        since_id = db[colname].find().limit(1).sort([('$natural',1)])[0]['id']
    else:
        since_id = -1

    return since_id

def _todb(colname, request):
    
    if (request.status_code != 200):
        logger.critical('StreamingApi.getJson status code %s \nrequest %s',
            request.status_code, request)
        raise Exception("Status code is not 200: ", request.status_code)
    else:
        db_name = __package__.replace('.', '_')
        logger.debug('filename:%s | db: %s | collection:%s | json: %s', __file__, db_name, colname, request.json())
        db = MongoClient(settings.MONGO_CLIENT)[db_name]
        json_list = request.json()
        # Duplicate removal
        for one_json in json_list:
            if (db[colname].find({'id' : one_json['id']}).count() == 0):
                db[colname].insert(one_json)
