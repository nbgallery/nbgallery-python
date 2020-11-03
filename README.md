# nbgallery-python

* Experimental work in progress - API subject to change! *

Python interface to a local nbgallery database

## Installation

 1. Install mysql client library; e.g. `default-libmysqlclient-dev` on Ubuntu.  Alternately, you may be able to use a different [mysql interface](https://docs.sqlalchemy.org/en/13/dialects/mysql.html) instead of `mysqlclient`.
 2. `pip install -r requirements.txt`

## Configuration

Create `nbgallery.cfg` in the current directory or `~/.config/nbgallery/`.  You can specify the nbgallery rails config file (e.g. `settings.local.yml`) to load settings from there instead.

```
[nbgallery]

rails_config =

mysql_username =
mysql_password = 
mysql_host =
mysql_port =
mysql_database =

notebook_cache_dir =
```

