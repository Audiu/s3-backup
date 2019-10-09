S3Backup
========

Flexible python based backup utility for storing to S3

About
-----

This is a small python script to handle performing backups cross
platform

Features
--------

It supports the following features:

-  Plan based backups
-  Custom command run pre-backup (can be used to perform complex pre-backup preparation tasks)
-  Storing to S3
-  Calculating MD5 hashes of the backup set to avoid uploading duplicate backup sets
-  Emailing the result of the backup plans
-  Python standard logging framework

Installation
------------

Install using ``pip``:

::

    pip install s3backup

Using ``virtualenv``:

::

    $ mkdir s3backup
    $ cd s3backup
    $ python3 -m venv .
    $ . bin/activate
    $ pip install -r requirements.txt

Dependencies
------------

S3Backup depends on:

- boto (AWS SDK)
- `glob2 <http://github.com/miracle2k/python-glob2/>`_ (Better file globbing)

Both can be installed via pip, however, if S3Backup is installed via pip then these dependencies will already be met.

Configuration
-------------

The backup utility is configured through the use of a JSON configuration
file

.. code:: json

    {
      "AWS_KEY": "this is a key",
      "AWS_SECRET": "this is a secret",
      "AWS_BUCKET": "this is a bucket",
      "AWS_REGION": "this is a region",
      "EMAIL_FROM": "source@address.com",
      "EMAIL_TO": "recipient@address.com",
      "HASH_CHECK_FILE": "plan_hashes.txt",
      "Plans": [
        {
          "Name": "MySQL Backup",
          "Command": "/home/bob/backups/backup-prep-script.sh",
          "Src": "/home/bob/backups/database/mysql_backup.sql",
          "OutputPrefix": "main_db",
          "PreviousBackupsCount": 2,
          "Zip64": false
        },
        {
          "Name": "Websites Backup",
          "Src": ["/var/www/html/website/**/*", "/var/www/html/website2/**/*"],
          "OutputPrefix": "websites_backup"
        }
      ]
    }

If emails are not required, then omit the ``EMAIL_FROM`` and
``EMAIL_TO`` fields of the configuration file.

If the ``PreviousBackupsCount`` is not set, then it will default to keeping
1 previous backup. It can be set to 0, which will only keep the current backup.

If the ``Zip64`` is not set, then it will default to ``true``. This allows for
Zip files > 2GB to be created. If running on a old environment this might need to
be forced to false.

*Note*: When on Windows, it is better to pass the paths using forward
slashes (/) as then escaping isn’t required (as with backslashes). The
script will normalize the paths in these cases. However, when providing
the command, if paths are required they will need to be double escaped.

There are more examples (including Windows examples) and further discussion
on `this blog post <https://mikegoodfellow.co.uk/s3-backup-utility/>`_

Usage
-----

You will need to set up an AWS account if you do not have one, and then
obtain AWS keys for an IAM account which has the following privileges:

-  S3 full access (for writing to the storage bucket)
-  SES full access (for sending emails)

Run the backup tool using the following method:

.. code:: python

    import logging
    import os
    import sys
    from S3Backup import S3BackupTool

    script_path = os.path.dirname(os.path.realpath(__file__)) + '/'

    # Log to file
    #logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    #                    filename=script_path + "s3backup.log", level=logging.INFO)

    # Log to stdout
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    s3backup = S3BackupTool("config.json")

    s3backup.run_plans()

See ``test.py`` for an example.

File Hashing
------------

After a backup set is created an MD5 hash is calculated for it. This is then compared against a previously calculated
hash for that particular plan name.

**NOTE:** Do not change the generated HASH_CHECK_FILE!

Finally, be aware of a "gotcha" - the hashes are keyed on the *plan name* - therefore changing the plan name will
cause the backup script to think it needs to upload a new backup set.

Emails
------

An email will be sent after each plan runs. The email will either report a success or a failure. In the event
of a success, it will be reported if there was a new uploaded backup set (and the file name), otherwise it will
state that no changes were detected and no upload was made.

If there was a failure while running the backup, the exception message will be emailed, and the logs can be
referred to for further information.

Future Improvements
-------------------

These are some of the planned future improvements:

-  Allow custom format strings for the output files (instead of the default date/time format)
-  Modification of the glob2 library to allow hidden files to be included
-  Allow exclude globs to be added when providing source directory
