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

import logging
from S3Backup import config_loader
from time import strftime, gmtime
import boto3

logger = logging.getLogger(name='S3BackupTool')


class S3BackupTool:

    def __init__(self, config_file="config.json"):
        logger.info('Initialising...')

        try:
            self.CONFIGURATION, self.PLANS = config_loader.config_setup(config_file)
        except Exception as e:
            logger.fatal('Failed to load configuration: %s', e)
            raise e

        logger.info('Loaded configuration')

    def run_plans(self):
        if len(self.PLANS) == 0:
            logger.warn('No plans to execute')
            return

        counter = 1
        for plan in self.PLANS:
            logger.info('Executing plan %d of %d', counter, len(self.PLANS))

            try:
                updated, output_file = plan.run()
                self.__send_success_email(plan, updated, output_file)
            except Exception as e:
                logger.error('Failed to run plan: %s', e)
                self.__send_failure_email(plan, e)

            counter += 1

        logger.info('Finished running backup plans')

    def __send_success_email(self, plan, updated, output_file):
        subject = '[S3-Backup] [SUCCESS] - Plan: %s' % plan.name

        body = 'The backup plan, %s, run at %s was SUCCESSFUL\n\n' % (
            plan.name,
            strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))

        if updated:
            body += 'The backup set had changed, so a new backup was uploaded: %s' % output_file
        else:
            body += 'The backup set had not changed. No new backup uploaded'

        self.__send_status_email(subject, body)

    def __send_failure_email(self, plan, exception):
        subject = '[S3-Backup] [FAILURE] - Plan: %s' % plan.name

        body = 'The backup plan, %s, run at %s was a FAILURE\n\n' % (
            plan.name,
            strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))

        body += '\n\nDetailed failure information:\n\n%s' % exception

        self.__send_status_email(subject, body)

    def __send_status_email(self, subject, body):
        if self.CONFIGURATION['EMAIL_FROM'] is None or self.CONFIGURATION['EMAIL_TO'] is None:
            logger.debug('Email not provided, so status update not sent')
            return

        ses_client = boto3.client(
            'ses',
            region_name=self.CONFIGURATION['AWS_REGION'],
            aws_access_key_id=self.CONFIGURATION['AWS_KEY'],
            aws_secret_access_key=self.CONFIGURATION['AWS_SECRET']
        )

        try:
            response = ses_client.send_email(
                Source=self.CONFIGURATION['EMAIL_FROM'],
                Destination={
                    'ToAddresses': [self.CONFIGURATION['EMAIL_TO']]
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': body,
                            'Charset': 'UTF-8'
                        }
                    }
                })

            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                logger.info('Successfully sent email to {0:s} with subject {1:s}'.format(self.CONFIGURATION['EMAIL_TO'],
                                                                                         subject))
            else:
                logger.error('Failed to send email to {0:s} with subject {1:s}'.format(self.CONFIGURATION['EMAIL_TO'],
                                                                                       subject))

        except Exception as e:
            logger.error('Failed to send email to {0:s} with subject {1:s}'.format(self.CONFIGURATION['EMAIL_TO'],
                                                                                   subject),
                         e)
