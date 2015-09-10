import mock as mock
from nose.tools import raises, assert_equals
from S3Backup import hash_file
from S3Backup.config_exception import ConfigException
from S3Backup.plan import Plan

class TestPlan:

    def setup(self):
        self.config = {
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

    @mock.patch('S3Backup.hash_file')
    def test_update_hash_should_try_to_store_new_hash(self, hash_file):
        self.new_hash = 'bob123'

        self.plan.__hash_check()
        hash_file.find_hash.assert_called_with('hashes.txt', 'my_backup', 'bob123')
        assert_equals(True, True)

