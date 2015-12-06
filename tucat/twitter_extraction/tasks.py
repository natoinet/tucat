from __future__ import absolute_import

import logging
import subprocess
from datetime import datetime
from os.path import dirname

from celery import task
from celery.app.task import Task

#from tucat.twitter_extraction.models import TwitterListExtraction, Manager, CustomTaskState, TwitterApp, TwitterUser
#from tucat.core.tasks import apilimit
from tucat.core.celery import app
#from tucat.application.models import CeleryTaskLock
from tucat.core.models import DjangoAdminCeleryTaskLock
from tucat.application.models import TucatApplication
from tucat.twitter_extraction.models import TwitterListExtraction, TwitterListExtractionExport
from tucat.twitter_extraction.twitter import tw_extraction

#from celery.signals import task_prerun, task_success, worker_init, task_failure

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
            tw_extraction(owner_name=element.owner_name, list_name=element.list_name)

        one_app.update(status='c')

    except Exception as e:
        logger.error('do_run exception %s', e)
        one_app.update(status='f')

    finally:
        lock.delete()

    return self.request.id

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
        export.link_file = output
        export.update(self.request.id, 'r')

        path = dirname(__file__) + '/export/'
        #export_type = ExportationType.objects.get(pk=export_type_id)
        logger.info('do_run_export %s %s %s to %s', export.export_type, export.collection, export.last_tweet, path)

        if (export.last_tweet is None):
            if (export.export_type.followers is True):
                #subprocess.call([path + 'followersgraph.sh', str(export.collection), path])
                output = subprocess.check_output([path + export.export_format.format + '-followersgraph.sh', str(export.collection), path])
            elif (export.export_type.friends is True):
                #subprocess.call([path + 'friendsgraph.sh', str(export.collection), path])
                output = subprocess.check_output([path + export.export_format.format + '-friendsgraph.sh', str(export.collection), path])
            else:
                logger.warning('do_run_export unknown export_type %s', export.export_type)
        else:
            epoch_lt = export.last_tweet.strftime('%s')
            logger.debug('do_run_export last_tweet epoch %s', epoch_lt)

            if (export.export_type.followers is True):
                #subprocess.call([path + 'followersgraph-lasttweet.sh', str(export.collection), epoch_lt, path])
                output = subprocess.check_output([path + export.export_format.format + '-followersgraph-lasttweet.sh', str(export.collection), epoch_lt, path])
            elif (export.export_type.friends is True):
                #subprocess.call([path + 'friendsgraph-lasttweet.sh', str(export.collection), epoch_lt, path])
                output = subprocess.check_output([path + export.export_format.format + '-friendsgraph-lasttweet.sh', str(export.collection), epoch_lt, path])
            else:
                logger.warning('do_run_export unknown export_type %s', export.export_type)

        logger.info('do_run_export output %s', output)
        export.link_file = output
        export.update(self.request.id, 'c')
    except Exception as e:
        logger.error('do_run_export exception %s', e)
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

'''
@task(bind=True)
def error_handler(self, uuid):
    result = self.app.AsyncResult(uuid)
    print('Task {0} raised exception: {1!r}\n{2!r}'.format(
          uuid, result.result, result.traceback))
'''

'''
class CallbackTask(Task):
  def on_success(self, retval, task_id, args, kwargs):
      print("on_success: ", task_id)
      task_extraction = CustomTaskState.objects.get(task_id=task_id)
      task_extraction.status = 'SUCCESS'
      task_extraction.save()

  def on_failure(self, exc, task_id, args, kwargs, einfo):
      print("on_success: ", task_id)
      task_extraction = CustomTaskState.objects.get(task_id=task_id)
      task_extraction.status = 'SUCCESS'
      task_extraction.save()
'''
'''
@task
def task_extraction_success(*args, **kwargs):
    print("task_extraction_success: %s %s" % (args, kwargs))
    #print("task_extraction_success: ", kwargs['task_id'])
    task_extraction = CustomTaskState.objects.get(task_id=kwargs['task_id'])
    task_extraction.status = 'SUCCESS'
    task_extraction.save()

    task_list_extraction = TwitterListExtraction.objects.get(task_id=kwargs['task_id'])
    task_list_extraction.status = 'SUCCESS'
    task_list_extraction.save()

@task
def task_extraction_failure(*args, **kwargs):
    print("task_extraction_failure: %s %s" % (args, kwargs))
    #print("task_extraction_failure: ", kwargs['task_id'])
    task_extraction = CustomTaskState.objects.get(task_id=kwargs['task_id'])
    task_extraction.status = 'FAILED'
    task_extraction.save()

    task_list_extraction = TwitterListExtraction.objects.get(task_id=kwargs['task_id'])
    task_list_extraction.status = 'FAILED'
    task_list_extraction.save()
'''
'''
@task(bind=True)
def many_twitter_list_extractions(self):
    # Level 1 tasks launched by a periodic task
    subtasks = []
    
    CustomTaskState.objects.create(name=self.name, task_id=self.request.id, status="STARTED")
    
    # Only one single manager is possible
    #manager = Manager.objects.all()[0]
    #manager.manager_status = 'STARTED'

    #Manager.objects.get(taskid=self.request.id).manager_status = 'STARTED'

    #For all enabled twitterListExtraction: Extract but synchronously
    many_enabled_lists = TwitterListExtraction.objects.filter(is_enabled=True)
    print("Start manyTwitterListExtractions: %s" % time.ctime())

    for single_list in many_enabled_lists:
        owner_name = single_list.list_owner
        list_name = single_list.list_name
        #subtasks.append(single_twitter_list_extraction.s(owner_name=owner_name, list_name=list_name))
        #singleTwitterListExtraction(owner_name, list_name)

    workflow = chain(*subtasks)
    #workflow.apply_async(link=task_extraction_success.s(task_id=self.request.id), 
    #    link_error=task_extraction_failure.s(task_id=self.request.id))
    workflow.apply_async()

    print ("End manyTwitterListExtractions: %s" % time.ctime())
'''

'''
@task(bind=True)
def single_twitter_list_extraction(self, *args, **kwargs):
    # Level 2 tasks launched by Level 1
    
    subtasks = []
    owner_name = kwargs['owner_name']
    list_name = kwargs['list_name']

    CustomTaskState.objects.create(name=self.name, task_id=self.request.id, status="STARTED")

    print ("Start singletwitterListExtraction: %s %s %s %s" % (self.request.id, time.ctime(), args, kwargs))
    filtered_single_model = TwitterListExtraction.objects.filter(
        list_owner=owner_name, list_name=list_name, is_enabled=True)

    single_model = TwitterListExtraction.objects.get(pk=filtered_single_model[0].id)

    print ("Single_Model: %s %s %s %s %s" % (single_model, single_model.list_owner, 
        single_model.list_name, single_model.task_id, single_model.status))

    single_model.task_id = self.request.id
    single_model.status = 'STARTED'
    result = single_model.save()

    print ("Single_Model saved %s %s %s %s %s" % (result, single_model.list_owner, 
        single_model.list_name, single_model.task_id, single_model.status))

    time.sleep(5)

    #get_members.apply_async(link=task_extraction_success.s(task_id=self.request.id), link_error=task_extraction_failure.s(task_id=self.request.id))

    try:
        #get_members.apply_async(link=task_extraction_success.s(task_id=self.request.id), link_error=task_extraction_failure.s(task_id=self.request.id))

        subtasks.append(get_members.s(args, kwargs))
        subtasks.append(get_followers.s(args, kwargs))
        subtasks.append(get_friends.s(args, kwargs))
        #subtasks.append(group([
        #                    get_followers.s(args, kwargs), 
        #                    get_friends.s(args, kwargs),]).s())
        subtasks.append(get_users.s(args, kwargs))
        #subtasks.append(task_extraction_success(self.request.id))
        workflow = chain(*subtasks)
        #workflow.apply_async()
        workflow.apply_async(link=task_extraction_success.s(task_id=self.request.id), 
            link_error=task_extraction_failure.s(task_id=self.request.id))
        #workflow.apply(link=task_extraction_success.s(task_id=self.request.id), 
        #    link_error=task_extraction_failure.s(task_id=self.request.id))
    except Exception as e:
        print ("Exception singletwitterListExtraction: %s %s" % (time.ctime(), e))

    print ("End singletwitterListExtraction: %s" % time.ctime())
    
    return
'''

'''
def single_twitter_list_extraction_success(sender, *args, **kwargs):
    TwitterListExtraction.objects.get(taskid=sender.id).list_status = 'SUCCESS'

def single_twitter_list_extraction_failure(sender, *args, **kwargs):
    TwitterListExtraction.objects.get(taskid=sender.id).list_status = 'FAILED'
'''

'''
@task
def get_members(*args, **kwargs):
    # Level 3 tasks launched by Level 2
    
    print("get_members")

    apilimit.s(url="https://api.twitter.com/1.1/lists/members.json").apply()

    tw_url = "https://api.twitter.com/1.1/lists/members.json"
    app_credential = TwitterApp.objects.filter(is_enabled=True)
    user_credentials = TwitterUser.objects.filter(is_enabled=True)

    apilimit.apply_async(url="https://api.twitter.com/1.1/lists/members.json", 
                        owner_screen_name=kwargs['owner_screen_name'], 
                        slug=kwargs['list_name'])

    #top_users_function = ApiLimitFunction(url, CONSUMER, TOKENS, parameters, PAGING_NAME, PAGING_KEY, REMAINING_KEY, RESET_EPOCH_KEY, addTopUsersToResults, {200 : 'ok', 401 : 'ok', 429 : 'wait'})

    for user_credential in user_credentials:
        apilimit.apply_async(url=tw_url, owner_screen_name=user_name, slug=list_name)

    return
'''

'''
@task
def get_followers(*args, **kwargs):
    # Level 3 tasks launched by Level 2
    
    print("get_followers")

    apilimit.s(url="https://api.twitter.com/1.1/followers/ids.json").apply()

    apilimit.apply_async(url="https://api.twitter.com/1.1/followers/ids.json", 
                        owner_screen_name=kwargs['owner_screen_name'], 
                        slug=kwargs['list_name'])

    for user_credential in user_credentials:
        apilimit.apply_async(url=tw_url, owner_screen_name=user_name, slug=list_name)

    return
'''
'''
@task
def get_friends(*args, **kwargs):
    # Level 3 tasks launched by Level 2

    print("get_friends")

    apilimit.s(url="https://api.twitter.com/1.1/friends/ids.json").apply()

    apilimit.apply_async(url="https://api.twitter.com/1.1/friends/ids.json", 
                        owner_screen_name=kwargs['owner_screen_name'], 
                        slug=kwargs['list_name'])

    for user_credential in user_credentials:
        apilimit.apply_async(url=tw_url, owner_screen_name=user_name, slug=list_name)
    
    return
'''
'''
@task
def get_users(*args, **kwargs):
    # Level 3 tasks launched by Level 2
    
    print("get_users")

    apilimit.s(url="https://api.twitter.com/1.1/users/lookup.json").apply()

    #apilimit.apply_async(url="https://api.twitter.com/1.1/users/lookup.json", 
    #                    owner_screen_name=kwargs['owner_screen_name'], 
    #                    slug=kwargs['list_name'])

    #for user_credential in user_credentials:
    #    apilimit.apply_async(url=tw_url, owner_screen_name=user_name, slug=list_name)

    #raise Exception('Exception', 'get_users')
    return
'''
'''
# PATCH FOR JUST ONE TYPE OF TASK TO BE SIGNALLED
@worker_init.connect
def on_worker_init(sender, **kwargs):
    task_failure.connect(many_twitter_list_extractions_failure, sender=sender.app.tasks[many_twitter_list_extractions.name])
    task_failure.connect(single_twitter_list_extraction_failure, sender=sender.app.tasks[single_twitter_list_extraction.name])

class CallbackTask(Task):
  def on_success(self, retval, task_id, args, kwargs):
      print('Hello world! Success: ' + self.name)

  def on_failure(self, exc, task_id, args, kwargs, einfo):
      print('Hello world! Failure: ' + self.name)


@task(base=CallbackTask)
def api_limit(*args, **kwargs):
    # Level 4 tasks launched by Level 3
    
    print ("Start api_limit: %s %s %s", time.ctime(), args, kwargs)

    #while (self.get_remaining() > 0):
    #    # Extract
    #    pass

    print ("End singletwitterListExtraction: %s" % time.ctime())
'''

