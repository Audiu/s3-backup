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

import json
import logging
from S3Backup.plan import Plan

logger = logging.getLogger(name='config_loader')

required_root_values = ['AWS_KEY', 'AWS_SECRET', 'AWS_BUCKET', 'AWS_REGION', 'HASH_CHECK_FILE', 'Plans']
optional_root_values = ['EMAIL_FROM', 'EMAIL_TO']


def config_setup(config_file):
    logger.info('Loading: %s', config_file)

    configuration = {
        'AWS_KEY': '',
        'AWS_SECRET': '',
        'AWS_BUCKET': '',
        'AWS_REGION': '',
        'HASH_CHECK_FILE': '',
        'EMAIL_FROM': None,
        'EMAIL_TO': None
    }

    plans = []

    with open(config_file) as json_data_file:
        data = json.load(json_data_file)

    failed = False

    # Test for root elements
    for required_value in required_root_values:
        if required_value not in data:
            failed = True
            logger.error('Missing required configuration value: %s', required_value)
        else:
            configuration[required_value] = data[required_value]

    for optional_value in optional_root_values:
        if optional_value in data:
            configuration[optional_value] = data[optional_value]

    if failed:
        raise Exception('Missing keys from data. See log for details.')

    for raw_plan in data['Plans']:
        plans.append(Plan(raw_plan, configuration))

    return configuration, plans
