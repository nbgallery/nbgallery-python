"""
Configuration to access a local nbgallery instance.

Configuration is loaded from a config file named nbgallery.yml, located in one
of the following directories (in order of precedence):

  * Current directory
  * User config directory (usually ~/.config/nbgallery/ on Linux)
  * Site config direcotries (e.g. /etc/xdg/nbgallery/)

The config file must specify mysql server parameters and the cache dir where
notebook document files are stored.  Optionally, you may instead specify the
location of the Rails config file, and this module will try to load the
relevant settings from there.

nbgallery:
  rails_config:
  mysql_username:
  mysql_password:
  mysql_host:
  mysql_port:
  mysql_database:
  notebook_cache_dir:
"""

from .loader import config_dirs
from .loader import config
from .loader import mysql_username, mysql_password, mysql_host, mysql_port, mysql_database
from .loader import mysql_url
from .loader import notebook_cache_dir
