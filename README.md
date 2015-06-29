# S3Backup

Flexible python based backup utility for storing to S3

## About

This is a small python script to handle performing backups cross platform

## Features

It supports the following features:

* Plan based backups
* Custom command run pre-backup
* Storing to S3
* Emailing the result of the backup plans
* Python standard logging framework

## Configuration

The backup utility is configured through the use of a JSON configuration file

```json
{
  "AWS_KEY": "this is a key",
  "AWS_SECRET": "this is a secret",
  "AWS_BUCKET": "this is a bucket",
  "AWS_REGION": "this is a region",
  "EMAIL_FROM": "source@address.com",
  "EMAIL_TO": "recipient@address.com",
  "Plans": [
    {
      "Name": "MySQL Backup",
      "Command": "mysqldump -u bob -p password > mysql_backup.sql",
      "Src": "c:/mysql_backup.sql",
      "OutputPrefix": "main_db"
    },
	{
      "Name": "Website Backup",
      "Src": ["c:/website/*.html", "C:/website/src/**/*"],
      "OutputPrefix": "website"
    }
  ]
}
```

If emails are not required, then omit the `EMAIL_FROM` and `EMAIL_TO` fields of the configuration file.

*Note*: When on Windows, it is better to pass the paths using forward slashes (/) as then escaping isn't required (as with backslashes). The script will normalize the paths in these cases. 
However, when providing the command, if paths are required they will need to be double escaped.

## Usage

You will need to set up an AWS account if you do not have one, and then obtain AWS keys for an IAM account which has the following privileges:

* S3 full access (for writing to the storage bucket)
* SES full access (for sending emails)

Run the backup tool using the following method:

```python
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
```

See `test.py` in the `src` folder for an example.

## Future Improvements

These are some of the planned future improvements:

* Run multiple pre-backup commands (by providing an array)