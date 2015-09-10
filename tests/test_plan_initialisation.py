from nose.tools import raises, assert_equals
from S3Backup.config_exception import ConfigException
from S3Backup.plan import Plan

class TestPlanInitialisation:

    def setup(self):
        self.config = {
        }

    @raises(ConfigException)
    def test_missing_required_values(self):
        plan_config = {
            'Name': 'my_backup',
            'Src': 'source/folder',
            'Command': 'do something',
            'PreviousBackupsCount': 2
        }

        plan = Plan(plan_config, self.config)

    def test_missing_optional_values(self):
        plan_config = {
            'Name': 'my_backup',
            'Src': 'source/folder',
            'OutputPrefix': 'test_'
        }

        plan = Plan(plan_config, self.config)

    def test_has_initialised_new_hash_to_none(self):
        plan_config = {
            'Name': 'my_backup',
            'Src': 'source/folder',
            'OutputPrefix': 'test_',
            'Command': 'do something',
            'PreviousBackupsCount': 2
        }

        plan = Plan(plan_config, self.config)
        assert_equals(plan.new_hash, None)

    def test_initialises_previous_backup_count_to_1_if_missing(self):
        plan_config = {
            'Name': 'my_backup',
            'Src': 'source/folder',
            'OutputPrefix': 'test_',
            'Command': 'do something'
        }

        plan = Plan(plan_config, self.config)
        assert_equals(plan.previous_backups_count, 1)

    def test_sets_previous_backup_count_according_to_setting(self):
        plan_config = {
            'Name': 'my_backup',
            'Src': 'source/folder',
            'OutputPrefix': 'test_',
            'Command': 'do something',
            'PreviousBackupsCount': 2
        }

        plan = Plan(plan_config, self.config)
        assert_equals(plan.previous_backups_count, 2)

