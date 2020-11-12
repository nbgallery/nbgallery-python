import appdirs
import os
from ruamel.yaml import YAML

# Config file order of precedence:
#  1. Current directory
#  2. User config directory
#  3. Site config directories
config_dirs = [os.getcwd()]
config_dirs.append(appdirs.user_config_dir('nbgallery'))
config_dirs += appdirs.site_config_dir('nbgallery', multipath=True).split(':')

# Load the first nbgallery.yml we find
yaml = YAML(typ='safe')
config = {}
for d in config_dirs:
    config_file = os.path.join(d, 'nbgallery.yml')
    if os.path.exists(config_file):
        with open(config_file) as f:
            config = yaml.load(f)
        break

if not config:
    raise ImportError(f"No nbgallery.yml config file found in the search path: {str(config_dirs)}")

# If the config lists a Rails config file, load that too and look for
# database configuration -- but our file takes precedence.
if config['nbgallery'].get('rails_config'):
    with open(config['nbgallery']['rails_config']) as f:
        rails_config = yaml.load(f)
    rails_mysql_config = rails_config.get('mysql', {})
    rails_directory_config = rails_config.get('directories', {})

    for s in ['username', 'password', 'host', 'port', 'database']:
        setting = 'mysql_' + s
        if not config['nbgallery'].get(setting):
            config['nbgallery'][setting] = rails_mysql_config.get(s)

    if not config['nbgallery'].get('notebook_cache_dir'):
        config['nbgallery']['notebook_cache_dir'] = rails_directory_config.get('cache') 

# Set mysql server defaults
if not config['nbgallery']['mysql_host']:
    config['nbgallery']['mysql_host'] = '127.0.0.1'
if not config['nbgallery']['mysql_port']:
    config['nbgallery']['mysql_port'] = '3306'

mysql_username = config['nbgallery']['mysql_username']
mysql_password = config['nbgallery']['mysql_password']
mysql_host = config['nbgallery']['mysql_host']
mysql_port = config['nbgallery']['mysql_port']
mysql_database = config['nbgallery']['mysql_database']
notebook_cache_dir = config['nbgallery']['notebook_cache_dir']

mysql_url = 'mysql+mysqldb://' + mysql_username
if mysql_password:
    mysql_url += ':' + mysql_password
mysql_url += '@' + mysql_host + ':' + str(mysql_port) + '/' + mysql_database
