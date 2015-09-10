import os
from nose.tools import raises, assert_true, assert_equals
from S3Backup import config_loader
from S3Backup.config_exception import ConfigException
from S3Backup.plan import Plan


class TestConfigLoader:

    @raises(IOError)
    def test_invalid_file(self):
        config_loader.config_setup('non_existent_file.bob')

    @raises(ValueError)
    def test_invalid_json(self):
        config_loader.config_setup(os.path.join('tests', 'json', 'test_bad.json'))

    @raises(ConfigException)
    def test_missing_required_value(self):
        config_loader.config_setup(os.path.join('tests', 'json', 'test_missing_required.json'))

    def test_missing_optional_value(self):
        config, plans = config_loader.config_setup(os.path.join('tests', 'json', 'test_missing_optional.json'))
        assert_true(config is not None, 'Config should be initialised')
        assert_true(isinstance(config, dict), 'Config should be a dictionary')
        assert_true(len(plans) == 2, 'There should be 2 plans')
        assert_true(isinstance(plans[0], Plan), 'Plan should be an instance of Plan')

    def test_complete_json(self):
        config, plans = config_loader.config_setup(os.path.join('tests', 'json', 'test.json'))
        assert_true(config is not None, 'Config should be initialised')
        assert_true(isinstance(config, dict), 'Config should be a dictionary')
        assert_equals(config['AWS_KEY'], 'this is a key')
        assert_equals(config['AWS_SECRET'], 'this is a secret')
        assert_equals(config['AWS_BUCKET'], 'this is a bucket')
        assert_equals(config['AWS_REGION'], 'this is a region')
        assert_equals(config['EMAIL_FROM'], 'source@address.com')
        assert_equals(config['EMAIL_TO'], 'recipient@address.com')
        assert_equals(config['HASH_CHECK_FILE'], 'plan_hashes.txt')

        assert_true(len(plans) == 2, 'There should be 2 plans')

        assert_true(isinstance(plans[0], Plan), 'Plan should be an instance of Plan')
        assert_equals(plans[0].CONFIGURATION, config)
        assert_equals(plans[0].name, 'MySQL Backup')
        assert_equals(plans[0].command, 'mysqldump -u bob -p password > mysql_backup.sql')
        assert_equals(plans[0].src, 'c:/mysql_backup.sql')
        assert_equals(plans[0].output_file_prefix, 'main_db')
        assert_equals(plans[0].previous_backups_count, 2)

        assert_true(isinstance(plans[1], Plan), 'Plan should be an instance of Plan')
        assert_equals(plans[1].CONFIGURATION, config)
        assert_equals(plans[1].name, 'Website Backup')
        assert_equals(plans[1].command, None)
        assert_equals(plans[1].src, ['c:/website/*.html', 'C:/website/src/**/*'])
        assert_equals(plans[1].output_file_prefix, 'website')
        assert_equals(plans[1].previous_backups_count, 1)
