import logging

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')

class TucatExportCommand(BaseCommand):
    '''
    Admin > User Command > TucatCommand.handle > ChildClass.do_cmd
    '''

    def add_arguments(self, parser):
        parser.add_argument('--obj', dest='obj')
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-r', '--run', action='store_true')
        group.add_argument('-s', '--stop', action='store_true')
        group.add_argument('-d', '--download', action='store_true')

    def handle(self, *args, **options):
        logger.info('Command Handle %s %s %s', str(self), args, options)

        if options['run']:
            logger.info('Running')
            self.do_cmd(action='run', obj=options['obj'])
        elif options['stop']:
            logger.info('Stopping')
            self.do_cmd(action='stop', obj=options['obj'])
        elif options['download']:
            logger.info('Downloading')
            self.do_cmd(action='download', obj=options['obj'])
        else:
            logger.info('Unknown command')

    def do_cmd(self, action=None):
        logger.info('do_cmd TucatExportCommand')
