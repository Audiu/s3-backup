from boto.s3.key import Key
import mock as mock
from nose.tools import raises, assert_equals
from S3Backup import hash_file
from S3Backup.config_exception import ConfigException
from S3Backup.plan import Plan
import subprocess

def mock_s3_key(func):
    def _mock_s3_key(*args, **kwargs):
        with mock.patch.object(Key, 'set_contents_from_filename', return_value=None):
            return func(*args, **kwargs)
    return _mock_s3_key

class TestPlan:

    def setup(self):
        self.config = {
            'AWS_KEY': 'key',
            'AWS_SECRET': 'secret',
            'AWS_REGION': 'region',
            'AWS_BUCKET': 'bucket',
            'HASH_CHECK_FILE': 'hashes.txt'
        }

        self.plan_config = {
            'Name': 'my_backup',
            'Src': 'source/folder',
            'OutputPrefix': 'test_',
            'Command': 'do something',
            'PreviousBackupCount': 2
        }

        self.plan = Plan(self.plan_config, self.config)

    '''@mock.patch('S3Backup.hash_file')
    def test_update_hash_should_try_to_store_new_hash(self, hash_file):
        self.new_hash = 'bob123'

        self.plan.__hash_check()
        hash_file.find_hash.assert_called_with('hashes.txt', 'my_backup', 'bob123')
        assert_equals(True, True)
    '''

    @mock_s3_key
    @mock.patch('boto.s3.connect_to_region')
    @mock.patch('zipfile.ZipFile.__enter__')
    @mock.patch('glob2.glob')
    @mock.patch('os.open')
    @mock.patch('subprocess.call')
    def test_command_defined_should_run_command(self, subprocess_call, os_open, glob2_glob, zipfile, boto_s3):
        bob = 'something'
        os_open.return_value = bob
        subprocess_call.return_value = 0

        glob2_glob.return_value = [
            'bob1'
        ]

        zipfile.return_value = MockZipFile()

        boto_s3.return_value = MockS3()

        self.plan.run()

        subprocess_call.assert_called_with(
            self.plan_config['Command'], shell=True, stdout=bob, stderr=subprocess_call.STDOUT)

    #@mock_s3_key
    @mock.patch('boto.s3.connect_to_region')
    @mock.patch('zipfile.ZipFile.__enter__')
    @mock.patch('glob2.glob')
    @mock.patch('os.open')
    @mock.patch('subprocess.call')
    def test_no_command_shouldnt_invoke_subprocess(self, subprocess_call, os_open, glob2_glob, zipfile, boto_s3):
        bob = 'something'
        os_open.return_value = bob
        subprocess_call.return_value = 0

        glob2_glob.return_value = [
            'bob1'
        ]

        zipfile.return_value = MockZipFile()

        boto_s3.return_value = MockS3()

        plan_config = {
            'Name': 'my_backup',
            'Src': 'source/folder',
            'OutputPrefix': 'test_',
            'PreviousBackupCount': 2
        }

        plan = Plan(plan_config, self.config)

        plan.run()

        assert not subprocess_call.called

class MockZipFile:
    def __init__(self):
        self.files = []
    def __iter__(self):
        return iter(self.files)
    def write(self, fname):
        self.files.append(fname)

class MockS3:
    def get_bucket(self, bucket_name):
        return 'bucket'

class MockKey:
    def set_contents_from_filename(self, filename):
        return None
