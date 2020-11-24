# nbgallery-python

**Experimental work in progress - API subject to change!**

Python interface to a local [nbgallery](https://github.com/nbgallery/nbgallery) database

## Motivation

 * Short-term: We want to analyze user behavior from a production nbgallery instance, but the system is written in Ruby and our data scientists are more comfortable with Python.
 * Medium-term: Our original production deployment had limited resources and flexibility, so our recommenders and other computation jobs were hand-rolled in Ruby.  We now have a containerized deployment, so this library can help us modernize and improve those jobs with Python data science packages.
 * Long-term: If we write nbgallery 2.0 in Python, this will potentially provide some building blocks.

## Library Overview

Please also see the [docs](docs) folder for some code examples.

### Database

The database submodule provides access to nbgallery's MySQL database through a couple different interfaces.

First, the Object-Relational Mapping (ORM) represents each row of the database as a Python object.  For example, a `Notebook` object `nb` corresponds to one row of the `notebooks` table, and you can access database fields as members of the object; e.g. `nb.title`.  The ORM automatically detects cross-table relationships; for example, `nb.creator` will return a `User` object representing a row in the `users` table.  The ORM interface mimics the `ActiveRecord` interface in Rails and is ideal for manipulating small numbers of objects in an intuitive way with minimal raw SQL.

Second, the dataframes interface returns pandas `DataFrame` objects containing large numbers of records.  These are intended as input for data science applications where you don’t need the object-per-row abstraction of the ORM. For example, you can obtain a dataframe containing counts of user-notebook interactions for use in user similarity computations or collaborative filtering recommenders.

### Notebooks

The notebooks submodule provides access to the notebook documents stored in nbgallery.  Currently, it is primarily a light abstraction on top of the interface provided by Jupyter’s `nbformat` module.  It’s intended as a way to obtain notebook content (code and markdown) for applications such as topic modeling or content-based recommenders.

## Installation

 1. Install the mysql client library; e.g. `default-libmysqlclient-dev` on Ubuntu or `mariadb-devel` on CentOS.  You may also need to install the Python devel package if you haven't already.
    * Alternately, you may be able to use a different [mysql interface](https://docs.sqlalchemy.org/en/13/dialects/mysql.html) instead of `mysqlclient`, but you'll need to modify `setup.py` too.
 2. From this directory, `pip install -e .` to install the `nbgallery` package in dev mode.  It is not published on PyPI yet.

## Configuration

Create `nbgallery.yml` in the current directory or `~/.config/nbgallery/`.  You can optionally specify the nbgallery Rails config file (e.g. `settings.local.yml`) to load database settings from there if not specified in `nbgallery.yml`.

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

