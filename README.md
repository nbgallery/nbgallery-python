# nbgallery-python

**Experimental work in progress - API subject to change!**

Python interface to a local [nbgallery](https://github.com/nbgallery/nbgallery) database

## Motivation

 * Short-term: We want to analyze user behavior from a production nbgallery instance, but the system is written in Ruby and our data scientists are more comfortable with Python.
 * Medium-term: Our original production deployment had limited resources and flexibility, so our recommenders and other computation jobs were hand-rolled in Ruby.  We now have a containerized deployment, so this library can help us modernize and improve those jobs with Python data science packages.
 * Long-term: If we write nbgallery 2.0 in Python, this will potentially provide some building blocks.

## Installation

 1. Install the mysql client library; e.g. `default-libmysqlclient-dev` on Ubuntu or `mariadb-devel` on CentOS.  You may also need to install the Python devel package if you haven't already.
    * Alternately, you may be able to use a different [mysql interface](https://docs.sqlalchemy.org/en/13/dialects/mysql.html) instead of `mysqlclient`, but you'll need to modify `setup.py` too.
 2. From this directory, `pip install -e .` to install the `nbgallery` package in dev mode.  It is not published on PyPI yet.

## Configuration

Create `nbgallery.yml` in the current directory or `~/.config/nbgallery/`.  You can specify the nbgallery rails config file (e.g. `settings.local.yml`) to load database settings from there if not specified in `nbgallery.yml`.

```
nbgallery:
  rails_config:
  mysql_username:
  mysql_password:
  mysql_host:
  mysql_port:
  mysql_database:
  notebook_cache_dir:
```

