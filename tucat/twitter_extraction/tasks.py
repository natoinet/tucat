from __future__ import absolute_import

import logging
import subprocess
from datetime import datetime
from os.path import dirname
from pathlib import Path
import re

from django.conf import settings
#from django.http import HttpResponse
#from django.core.files import File

#from private_storage.fields import PrivateFileField

from celery import task
from celery.app.task import Task

from tucat.core.celery import app
from tucat.core.models import DjangoAdminCeleryTaskLock
from tucat.application.models import TucatApplication
from tucat.twitter_extraction.models import TwitterListExtraction, TwitterListExtractionExport, ExtractionCollection
from tucat.twitter_extraction.twitter import tw_extraction, get_collection


logger = logging.getLogger('twitter_extraction')

@task(bind=True)
def do_run_extraction(self, obj_pk):
    try:
        logger.info('do_run')

        task_id = self.request.id
        #lock = CeleryTaskLock(package_name=__package__, task_id=task_id)
        #lock.save()

        md5_hash = DjangoAdminCeleryTaskLock.hash(__package__, 'extraction')
        lock = DjangoAdminCeleryTaskLock(task_id=task_id, md5_hex=md5_hash)
        lock.save()

        #one_app = TucatApplication.objects.get(package_name=__package__)
        one_app = TucatApplication.objects.get(pk=obj_pk)
        one_app.update(task_id=task_id, status='r')

        tucat_elements = TwitterListExtraction.objects.filter(application_id=one_app.id, is_enabled=True)
        for element in tucat_elements:
            colname = "-".join([element.owner_name, element.list_name, datetime.utcnow().strftime('%Y-%m-%d-%H-%M')])
            tw_extraction(owner_name=element.owner_name, list_name=element.list_name, collection_name=colname)
            ExtractionCollection.objects.create_collection(element.owner_name, element.list_name, datetime.now(), colname)
            add_dt_to_mongo(colname)

        one_app.update(status='c')

    except Exception as e:
        logger.exception(e)
        one_app.update(status='f')

    finally:
        lock.delete()

    return self.request.id

def add_dt_to_mongo(col_name):
    logger.info('add_dt')

    try:
        db_name = __package__.replace('.', '_')
        collection = get_collection(db_name, col_name)

        for doc in collection.find():
            doc['dtcreatedat'] = get_dt( doc['createdat'] )
            doc['dtstatuscreatedat'] = get_dt( doc['statuscreatedat'] )
            collection.replace_one({'_id': doc['_id']}, doc)

    except Exception as e:
        logger.exception(e)

def get_dt(date_val):
    dt_val = datetime.fromtimestamp(0)
    try:
        if (date_val is not None):
            dt_val = datetime.strptime(date_val, '%a %b %d %H:%M:%S %z %Y')
    except Exception as e:
        logger.exception(e)
    return dt_val

def do_stop_extraction(obj_pk):
    try:
        #lock = CeleryTaskLock.objects.get(package_name=__package__)
        lock_hash = DjangoAdminCeleryTaskLock.hash(__package__, 'extraction')
        lock = DjangoAdminCeleryTaskLock.objects.get(md5_hex=lock_hash)

        logger.info('do_stop locked task_id %s', lock.task_id)
        app.control.revoke(lock.task_id, terminate=True)
        lock.delete()
        logger.info('do_stop: Task revoked and lock released')

        #one_app = TucatApplication.objects.get(package_name=__package__)
        one_app = TucatApplication.objects.get(pk=obj_pk)
        one_app.update(status='s')

    except Exception as e:
        logger.error('do_stop exception %s', e)

def unlock_extraction(obj_pk):
    try:
        #lock = CeleryTaskLock.objects.get(package_name=__package__).delete()
        lock_hash = DjangoAdminCeleryTaskLock.hash(__package__, 'extraction')
        DjangoAdminCeleryTaskLock.objects.get(md5_hex=lock_hash).delete()

        #one_app = TucatApplication.objects.get(package_name=__package__)
        one_app = TucatApplication.objects.get(pk=obj_pk)
        one_app.update(status='f', lock=None)
        logger.info('unlock> %s unlocked', one_app.name)
    except Exception as e:
        logger.error('unlock exception %s', e)

def do_extraction_cmd(action=None, obj=None):
    logger.info('do_cmd %s %s', action, obj)

    if (action is 'run'):
        logger.info('Running')
        do_run_extraction.apply_async((obj.pk,))
    elif (action is 'stop'):
        logger.info('Stopping')
        do_stop_extraction(obj.pk)
    elif (action is 'unlock'):
        logger.info('Unlocking')
        unlock_extraction(obj.pk)
    else:
        logger.info('Unknown command')

@task(bind=True)
def do_run_export(self, obj_pk):
    logger.info('do_run_export')
    export = TwitterListExtractionExport.objects.get(pk=obj_pk)

    try:
        output = None
        db_name = __package__.replace('.', '_')
        out_folder = str(Path(__file__).parents[1] / 'output')
        export.link_file = output
        export.update(self.request.id, 'r')

        path = str(Path(__file__).parent / 'export') + '/'
        #export_type = ExportationType.objects.get(pk=export_type_id)
        logger.info('do_run_export %s %s %s to %s', export.export_type, export.collection, export.last_tweet, path)

        if (export.last_tweet is None):
            if (export.export_type.followers is True):
                #subprocess.call([path + 'followersgraph.sh', str(export.collection), path])
                output = subprocess.check_output([path + export.export_format.format + '-followersgraph.sh', db_name, str(export.collection), path, out_folder])
            elif (export.export_type.friends is True):
                #subprocess.call([path + 'friendsgraph.sh', str(export.collection), path])
                output = subprocess.check_output([path + export.export_format.format + '-friendsgraph.sh', db_name, str(export.collection), path, out_folder])
            else:
                logger.warning('do_run_export unknown export_type %s', export.export_type)
        else:
            epoch_lt = export.last_tweet.strftime('%s') + '000'
            logger.debug('do_run_export last_tweet epoch %s', epoch_lt)

            if (export.export_type.followers is True):
                #subprocess.call([path + 'followersgraph-lasttweet.sh', str(export.collection), epoch_lt, path])
                output = subprocess.check_output([path + export.export_format.format + '-followersgraph-lasttweet.sh', db_name, str(export.collection), epoch_lt, path, out_folder])
            elif (export.export_type.friends is True):
                #subprocess.call([path + 'friendsgraph-lasttweet.sh', str(export.collection), epoch_lt, path])
                output = subprocess.check_output([path + export.export_format.format + '-friendsgraph-lasttweet.sh', db_name, str(export.collection), epoch_lt, path, out_folder])
            else:
                logger.warning('do_run_export unknown export_type %s', export.export_type)

        logger.info('do_run_export output %s', output)
        #export.link_file = output.decode("utf-8")

        result = output.decode("utf-8")
        export.link_file = re.findall(r"\S+", result)[1]

        export.update(self.request.id, 'c', link_file=export.link_file)
    except Exception as e:
        logger.exception(e)
        export.update(self.request.id, 'f')

def do_stop_export(obj_pk):
    logger.info('do_stop_export')
    export = TwitterListExtractionExport.objects.get(pk=obj_pk)

    try:
        logger.info('do_stop_export locked task_id %s', export.task_id)
        app.control.revoke(export.task_id, terminate=True)
        logger.info('do_stop_export: Task revoked')

        export.update('', 's')

    except Exception as e:
        logger.error('do_stop exception %s', e)

def do_export_cmd(action=None, obj=None):
    logger.info('do_export_cmd %s %s %s %s %s', action, obj, obj.export_type, obj.collection, obj.last_tweet)

    if (action is 'run'):
        logger.info('do_export_cmd running')
        do_run_export.apply_async((obj.pk,))

#        do_run_export.apply_async(kwargs={'export_type_id': obj.export_type.pk, 'collection': obj.collections.pk, 'last_tweet' : obj.last_tweet})
    elif (action is 'stop'):
        logger.info('do_export_cmd stopping')
        do_stop_export(obj.pk)
    else:
        logger.info('Unknown command')
