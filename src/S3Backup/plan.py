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

required_plan_values = ['Name', 'Src', 'Output']
optional_plan_values = ['Command']

logger = logging.getLogger(name='Plan')

class Plan:

    def __init__(self, raw_plan):
        failed = False

        for required_value in required_plan_values:
            if required_value not in raw_plan:
                failed = True
                logger.error('Missing plan configuration value: %s', required_value)

        self.name = raw_plan['Name']
        self.src = raw_plan['Src']
        self.output = raw_plan['Output']
        self.command = None

        if 'Command' in raw_plan:
            self.command = raw_plan['Command']

        if failed:
            raise Exception('Missing keys from data. See log for details.')

    def run(self):
        logger.info('Running plan "%s"', self.name)
