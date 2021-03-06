import yaml
from os import path, environ


def contains(small, big):
    for v in small:
        if v not in big:
            return False
    return True


def is_debug():
    return environ.get('DEBUG', 'False') != 'False'


def initialize_config(config_file_name='env.yaml'):
    config_keys = ['DBSERVER', 'DBNAME', 'DBUSER', 'DBPASS', 'DBPORT', 'REDISHOST', 'REDISPORT', 'REDISPASS']
    if contains(config_keys, list(environ.keys())):
        environ['DEBUG'] = 'False'
        return

    config_file_path = path.join(path.dirname(path.abspath(__file__)), config_file_name)

    if not path.exists(config_file_path):
        raise Exception('env.yaml required for config initialization')
    
    with open(config_file_path, 'r') as config_file:
        config = yaml.load(config_file)
        config['dbconfig']['DBPORT'] = str(config['dbconfig']['DBPORT'])
        config['redisconfig']['REDISPORT'] = str(config['redisconfig']['REDISPORT'])
        environ.update(config['dbconfig'])
        environ.update(config['redisconfig'])
        environ['DEBUG'] = 'True'
