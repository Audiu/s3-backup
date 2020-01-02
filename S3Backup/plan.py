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
import sys

import boto3
import glob2
import logging
import os
import subprocess
from zipfile import ZipFile
import time
from S3Backup import hash_file

required_plan_values = ['Name', 'Src', 'OutputPrefix']
optional_plan_values = ['Command', 'PreviousBackupsCount', 'Zip64']

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

        if 'PreviousBackupsCount' in raw_plan:
            self.previous_backups_count = int(raw_plan['PreviousBackupsCount'])
        else:
            self.previous_backups_count = 1

        if 'Zip64' in raw_plan:
            self.zip64 = bool(raw_plan['Zip64'])
        else:
            self.zip64 = True

        self.output_file_prefix = raw_plan['OutputPrefix']
        self.output_file = '%s_%s.zip' % (raw_plan['OutputPrefix'], time.strftime("%Y-%m-%d_%H-%M-%S"))

        self.new_hash = None

        if 'Command' in raw_plan:
            self.command = raw_plan['Command']

        if failed:
            raise Exception('Missing keys from data. See log for details.')

    def run(self):
        """
            The plan is run in the following order:
                1) (if applicable) Run the external command provided
                2) Zip source file(s) to destination file
                3) Perform hash check to see if there are any changes (which would require an upload)
                4) Upload destination file to S3 bucket
                5) Update hash file with new hash
                6) Check if any previous backups need removing
        """
        logger.info('Running plan "%s"', self.name)

        # 1) (if applicable) Run the external command provided
        if self.command is not None:
            self.__run_command()

        # 2) Zip the source file to the destination file
        self.__zip_files()

        updated = False

        try:
            # 3) Perform hash check to see if there are any changes (which would require an upload)
            if not self.__hash_check():
                # 4) Upload destination file to S3 bucket
                self.__upload()

                # 5) Update hash file with new hash
                self.__update_hash()

                updated = True

            # 6) Remove any previous backups if required
            self.__clear_old_backups()

        finally:
            self.__cleanup()

        return updated, self.output_file

    def __run_command(self):
        logger.info('Executing custom command...')

        try:
            command_path = self.command

            if self.command[0] is not '/':
                command_path = os.path.join(sys.path[0], self.command)

            logger.info('Executing %s', command_path)

            fnull = open(os.devnull, "w")
            retcode = subprocess.call(command_path, shell=True, stdout=fnull, stderr=subprocess.STDOUT)

            logger.info('Process returned code %d', retcode)

            if retcode != 0:
                raise Exception('Failed with code %d' % retcode)

        except subprocess.CalledProcessError as e:
            logger.error('Failed with code %d : %s', e.returncode, e.output)
            raise

    def __zip_files(self):
        fileset = []

        if isinstance(self.src, list):
            for src_path in self.src:
                normalized_src = os.path.normpath(src_path)
                if src_path[0] is not '/':
                    normalized_src = os.path.normpath(os.path.join(sys.path[0], src_path))

                for filename in glob2.glob(normalized_src):
                    fileset.append(filename)
        else:
            normalized_src = os.path.normpath(self.src)
            if self.src[0] is not '/':
                normalized_src = os.path.join(sys.path[0], self.src)

            for filename in glob2.glob(normalized_src):
                fileset.append(filename)

        # Check there are files in the file set
        if len(fileset) == 0:
            raise Exception('No input files retrieved from pattern: %s' % self.src)

        logger.info('Outputting to %s', self.output_file)

        with ZipFile(self.output_file, 'w', allowZip64=self.zip64) as myzip:
            for file_name in fileset:
                try:
                    logger.debug('Adding: %s', file_name)
                    myzip.write(file_name)
                except Exception as e:
                    logger.error('Error while adding file to the archive: %s - %s', file_name, e)
                    raise

        logger.info('Output file created')

    def __clear_old_backups(self):
        try:
            s3_client = boto3.client(
                's3',
                region_name=self.CONFIGURATION['AWS_REGION'],
                aws_access_key_id=self.CONFIGURATION['AWS_KEY'],
                aws_secret_access_key=self.CONFIGURATION['AWS_SECRET']
            )

            backup_keys = []

            for key in s3_client.list_objects(Bucket=self.CONFIGURATION['AWS_BUCKET'],
                                              Prefix=self.output_file_prefix)['Contents']:
                backup_keys.append(key['Key'])

            backup_keys.sort()

            logger.info('There are %d previous backups', len(backup_keys))

            max_backups = self.previous_backups_count + 1  # Because this is run after current backup uploaded

            if len(backup_keys) > max_backups:
                backups_to_remove = len(backup_keys) - max_backups
                logger.info('Removing %d previous backups', backups_to_remove)

                for i in range(backups_to_remove):
                    logger.info('Removing previous backup: %s', backup_keys[i])
                    s3_client.delete_object(Bucket=self.CONFIGURATION['AWS_BUCKET'], Key=backup_keys[i])
            else:
                logger.info('No previous backups require removal')

        except Exception as e:
            logger.error('Failed to clear out previous backups from S3: %s', e)
            raise

    def __upload(self):
        try:
            s3_client = boto3.client(
                's3',
                region_name=self.CONFIGURATION['AWS_REGION'],
                aws_access_key_id=self.CONFIGURATION['AWS_KEY'],
                aws_secret_access_key=self.CONFIGURATION['AWS_SECRET']
            )

            tc = boto3.s3.transfer.TransferConfig()
            t = boto3.s3.transfer.S3Transfer(client=s3_client,
                                             config=tc)

            t.upload_file(self.output_file, self.CONFIGURATION['AWS_BUCKET'], self.output_file)

        except Exception as e:
            logger.error('Failed to upload backup file to S3: %s', e)
            raise

    def __hash_check(self):
        previous_hash = hash_file.find_hash(self.CONFIGURATION['HASH_CHECK_FILE'], self.name)

        if previous_hash is None:
            logger.debug('No previous hash found for plan %s', self.name)
        else:
            logger.debug('Got a previous hash for plan %s of %s', self.name, previous_hash)

        self.new_hash = hash_file.calc_hash(self.output_file)

        logger.debug('New hash for plan %s of %s', self.name, self.new_hash)

        return previous_hash == self.new_hash

    def __update_hash(self):
        if self.new_hash is None:
            logger.error('Could not update hash as no hash was found')
            return

        hash_file.update_hash(self.CONFIGURATION['HASH_CHECK_FILE'], self.name, self.new_hash)

    def __cleanup(self):
        logger.info('Cleaning up temporary file: %s', self.output_file)
        try:
            if os.path.isfile(self.output_file):
                os.remove(self.output_file)
        except Exception as e:
            logger.error('Failed to remove temporary file: %s', e)
