import logging
import os
import sys
from S3Backup import S3BackupTool

script_path = os.path.dirname(os.path.realpath(__file__)) + '/'

#logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
#                    filename=script_path + "s3backup.log", level=logging.INFO)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

s3backup = S3BackupTool("test.json")

s3backup.run_plans()
