import logging
from S3Backup import config_loader

logger = logging.getLogger(name='S3BackupTool')

class S3BackupTool:

    def __init__(self, config_file="config.json", log_file="s3backup.log"):
        logger.info('Initialising...')

        try:
            self.CONFIGURATION = config_loader.config_setup(config_file)
        except Exception, e:
            logger.fatal('Failed to load configuration: %s', e)
            raise e

        logger.info('Loaded configuration')

    def run_plans(self):
        if len(self.CONFIGURATION['Plans']) == 0:
            logger.warn('No plans to execute')
            return

        counter = 1
        for plan in self.CONFIGURATION['Plans']:
            logger.info('Executing plan %d of %d', counter, len(self.CONFIGURATION['Plans']))
