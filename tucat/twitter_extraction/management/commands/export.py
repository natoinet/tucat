import logging

from tucat.core.commands import TucatExportCommand
from tucat.twitter_extraction.tasks import do_export_cmd

logger = logging.getLogger('twitter_extraction')

class Command(TucatExportCommand):
    '''
    Admin > User Command > TucatExportCommand.handle > do_cmd > do_export_cmd
    '''

    def do_cmd(self, action=None, obj=None):
        do_export_cmd(action=action, obj=obj)
