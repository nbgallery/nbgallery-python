import appdirs
import configparser
import os
from ruamel.yaml import YAML

config_dirs = appdirs.site_config_dir('nbgallery', multipath=True).split(':')
config_dirs.append(appdirs.user_config_dir('nbgallery'))
config_dirs.append(os.getcwd())

config = configparser.ConfigParser()
config.read([os.path.join(p, 'nbgallery.cfg') for p in config_dirs])
config = config['nbgallery']

rails_config = {}
yaml = YAML(typ='safe')
if config.get('rails_config'):
    with open(config['rails_config']) as f:
        rails_config = yaml.load(f)

rails_mysql_config = rails_config.get('mysql', {})
rails_directory_config = rails_config.get('directories', {})

mysql_username = config['mysql_username'] or rails_mysql_config.get('username')
mysql_password = config['mysql_password'] or rails_mysql_config.get('password')
mysql_host = config['mysql_host'] or rails_mysql_config.get('host') or '127.0.0.1'
mysql_port = config['mysql_port'] or rails_mysql_config.get('port') or '3306'
mysql_database = config['mysql_database'] or rails_mysql_config.get('database')
notebook_cache_dir = config['notebook_cache_dir'] or rails_directory_config.get('cache')

mysql_url = 'mysql+mysqldb://' + mysql_username
if mysql_password:
    mysql_url += ':' + mysql_password
mysql_url += '@' + mysql_host + ':' + mysql_port + '/' + mysql_database
