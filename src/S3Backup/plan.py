"""
The MIT License (MIT)

Copyright (c) 2015 Mike Goodfellow

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from boto.s3.key import Key
import glob2
import logging
import os
import subprocess
from zipfile import ZipFile
import time
import boto.ses

required_plan_values = ['Name', 'Src', 'OutputPrefix']
optional_plan_values = ['Command']

logger = logging.getLogger(name='Plan')

class Plan:

    def __init__(self, raw_plan, configuration):
        failed = False

        for required_value in required_plan_values:
            if required_value not in raw_plan:
                failed = True
                logger.error('Missing plan configuration value: %s', required_value)

        self.CONFIGURATION = configuration

        self.name = raw_plan['Name']
        self.src = raw_plan['Src']
        self.command = None
        self.output_file = '%s_%s.zip' % (raw_plan['OutputPrefix'], time.strftime("%Y-%m-%d_%H-%M-%S"))

        if 'Command' in raw_plan:
            self.command = raw_plan['Command']

        if failed:
            raise Exception('Missing keys from data. See log for details.')

    def run(self):
        """
            The plan is run in the following order:
                1) (if applicable) Run the external command provided
                2) Zip source file(s) to destination file
                3) Upload destination file to S3 bucket
        """
        logger.info('Running plan "%s"', self.name)

        # 1) (if applicable) Run the external command provided
        if self.command is not None:
            self.__run_command()

        # 2) Zip the source file to the destination file
        self.__zip_files()

        # 3) Upload destination file to S3 bucket
        try:
            self.__upload()
        finally:
            self.__cleanup()

    def __run_command(self):
        logger.info('Executing custom command...')

        try:
            fnull = open(os.devnull, "w")
            retcode = subprocess.call(self.command, shell=True, stdout=fnull, stderr=subprocess.STDOUT)

            if retcode != 0:
                raise Exception('Failed with code %d' % retcode)

        except subprocess.CalledProcessError, e:
            logger.error('Failed with code %d : %s', e.returncode, e.output)
            raise

    def __zip_files(self):
        fileset = []
        if isinstance(self.src, list):
            for src_path in self.src:
                for filename in glob2.glob(os.path.normpath(src_path)):
                    fileset.append(filename)
        else:
            for filename in glob2.glob(os.path.normpath(self.src)):
                fileset.append(filename)

        # Check there are files in the file set
        if len(fileset) == 0:
            raise Exception('No input files retrieved from pattern: %s' % self.src)

        logger.info('Outputting to %s', self.output_file)

        with ZipFile(self.output_file, 'w') as myzip:
            for file_name in fileset:
                try:
                    logger.debug('Adding: %s', file_name)
                    myzip.write(file_name)
                except Exception, e:
                    logger.error('Error while adding file to the archive: %s - %s', file_name, e)
                    raise

        logger.info('Output file created')

    def __upload(self):
        try:
            conn = boto.s3.connect_to_region(
                self.CONFIGURATION['AWS_REGION'],
                aws_access_key_id=self.CONFIGURATION['AWS_KEY'],
                aws_secret_access_key=self.CONFIGURATION['AWS_SECRET'])

            bucket = conn.get_bucket(self.CONFIGURATION['AWS_BUCKET'])

            key = Key(bucket)
            key.key = self.output_file
            key.set_contents_from_filename(self.output_file)
        except Exception, e:
            logger.error('Failed to upload backup file to S3: %s', e)
            raise

    def __cleanup(self):
        logger.info('Cleaning up temporary file: %s', self.output_file)
        try:
            if os.path.isfile(self.output_file):
                os.remove(self.output_file)
        except Exception, e:
            logger.error('Failed to remove temporary file: %s', e)
