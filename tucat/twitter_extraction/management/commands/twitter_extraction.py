import logging

from tucat.application.commands import TucatCommand
from tucat.twitter_extraction.tasks import do_extraction_cmd

logger = logging.getLogger('twitter_extraction')

class Command(TucatCommand):
    '''
    Admin > User Command > TucatCommand.handle > do_cmd > do_extraction_cmd
    '''
    
    def do_cmd(self, action=None, obj=None):
        do_extraction_cmd(action, obj=obj)
