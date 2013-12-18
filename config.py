import yaml
from os import path, environ

def initialize_config(config_file_name='env.yaml'):
    config_file_path = path.join(path.dirname(path.abspath(__file__)), config_file_name)

    if not path.exists(config_file_path):
        raise Exception('env.yaml required for config initialization')
    
    with open(config_file_path, 'r') as config_file:
        config = yaml.load(config_file)
        environ.update(config['dbconfig'])
