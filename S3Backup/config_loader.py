import json
import logging

logger = logging.getLogger(name='config_loader')

required_root_values = ['AWS_KEY', 'AWS_SECRET']
required_plan_values = []

def config_setup(config_file):
    logger.info('Loading: %s', config_file)

    configuration = {
        'AWS_KEY': '',
        'AWS_SECRET': '',
        'Plans': []
    }

    with open(config_file) as json_data_file:
        data = json.load(json_data_file)
    print(data)

    failed = False

    # Test for root elements
    for required_value in required_root_values:
        if required_value not in data:
            failed = True
            logger.error('Missing required configuration value: %s', required_value)
        else:
            configuration[required_value] = data[required_value]

    print(configuration)

    if failed:
        raise Exception('Missing keys from data. See log for details.')

    return configuration
