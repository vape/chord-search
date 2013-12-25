import yaml
from os import path, environ

def contains(small, big):
    for i in range(1 + len(big) - len(small)):
        if small == big[i:i+len(small)]:
            return i, i + len(small) - 1
    return False

def initialize_config(config_file_name='env.yaml'):
    config_keys = ['DBSERVER', 'DBNAME', 'DBUSER', 'DBPASS', 'DBPORT']
    if contains(config_keys, environ.keys()):
        return

    config_file_path = path.join(path.dirname(path.abspath(__file__)), config_file_name)

    if not path.exists(config_file_path):
        raise Exception('env.yaml required for config initialization')
    
    with open(config_file_path, 'r') as config_file:
        config = yaml.load(config_file)
        environ.update(config['dbconfig'])
