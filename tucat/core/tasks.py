from __future__ import absolute_import

import time

from celery import shared_task
from celery.app.task import Task
from celery.signals import task_success, worker_init


'''
@shared_task(name='apilimit')
def apilimit(*args, **kwargs):
    # Level 4 tasks launched by Level 3
    
    #time.sleep(5)
    print("apilimit: %s %s " % (args, kwargs))
    return kwargs
'''
'''
def apilimit_success(sender, *args, **kwargs):
    print('apilimit_success start: %s %s %s' % (sender.name, args, kwargs))

    kwargs.pop('signal', None)
    result = kwargs.pop('result', None)
    print('apilimit_success result: %s' % result)
    
    apilimit.s(**result).apply_async(countdown=10)
'''
'''
    if kwargs['remaining'] > 0:
        apilimit.s(kwargs).apply_async(countdown=1)
    else:
        parentid = kwargs['parentids']
        result = app.AsyncResult(parentid)
        result.status = 'SUCCESS'
'''
'''
    print('apilimit_success stop: %s' % sender.name)

# PATCH FOR JUST ONE TYPE OF TASK TO BE SIGNALLED
@worker_init.connect
def on_worker_init(sender, *args, **kwargs):
    task_success.connect(apilimit_success, sender=sender.app.tasks[apilimit.name])
'''

'''
class CallbackTask(Task):
  def on_success(self, retval, task_id, args, kwargs):
      print('apilimit on_success: %s %s %s %s' % (self.name , retval, args , kwargs))
      apilimit.s(**retval).apply_async(countdown=10)

  def on_failure(self, exc, task_id, args, kwargs, einfo):
      print('apilimit on_failure: %s %s %s %s %s %s' % (self.name , exc, task_id, args, kwargs, einfo))
'''

'''
#@shared_task(bind=True, name='apilimit', base=CallbackTask)
@shared_task(bind=True, name='apilimit')
def apilimit(self, *args, **kwargs):
    # Level 4 tasks launched by Level 3
    
    print ("Start api_limit: %s %s %s" % (time.ctime() , args , kwargs))

    #time.sleep(5)

    self.retry(countdown=5, max_retries=5)

    print ("End apilimit: %s" % time.ctime())

    return kwargs
'''