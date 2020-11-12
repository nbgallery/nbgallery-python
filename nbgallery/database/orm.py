"""
Object-relational mapping for nbgallery database.

Use this module to access the database with Python objects that map to rows in
the database. The naming convention is similar to Rails ActiveRecord where
possible.  For example, the Notebook object maps to an entry in the 'notebooks'
database table.
"""

import sqlalchemy as sa
import sqlalchemy.orm
import sqlalchemy.ext.automap
import sqlalchemy_utils as sa_utils
import sqlalchemy_mixins as sa_mixins

import nbgallery.database as nbgdb

#
# Automap
# 
# https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html
#
# This module uses SQLAlchemy's ORM Automap extension to automatically generate
# Python classes from the existing nbgallery database, which is created by Rails.
# We've partially declared some of the classes below for cases when the Automap
# doesn't quite handle the structure or we need to customize the class creation.
# The rest of the classes are automatically generated in full and end up listed
# in the Base class.  We then pull all those up into this module namespace.
#

#
# Polymorphic associations / generic releationships
#
# This is an association where one table can point to multiple different tables.
# As an example, in nbgallery, a Notebook can be owned by a User or a Group.
# This is implemented by having an owner_type field, which specifies the class
# (and database table) of the owner, and owner_id, which specifies the entry
# in that table.
#
# Rails calls them polymorphic associations:
# https://guides.rubyonrails.org/association_basics.html#polymorphic-associations
#
# SQLAlchemy also has polymorphic associations but those are a little different;
# the more direct analog to Rails is "generic associations":
# https://docs.sqlalchemy.org/en/13/orm/examples.html#module-examples.generic_associations
#
# We're using a helper from the sqlalchemy-utils package to implement it:
# https://sqlalchemy-utils.readthedocs.io/en/latest/generic_relationship.html
#
# Just for completeness, Django calls them generic relations:
# https://docs.djangoproject.com/en/3.1/ref/contrib/contenttypes/#generic-relations
#

# Session class for ORM usage
Session = sa.orm.sessionmaker(bind=nbgdb.engine)

# The Automap base class
Base = sa.ext.automap.automap_base()

# Add in a Mixin so classes will print out more nicely - but note we have to
# partially declare any classes that we want to use this.
class BaseModel(Base, sa_mixins.ReprMixin):
    __abstract__ = True
    __repr__ = sa_mixins.ReprMixin.__repr__
    pass

class Notebook(BaseModel):
    __tablename__ = 'notebooks'
    __repr_attrs__ = ['title']
    __repr_max_length__ = 45

    # Custom relationships that Automap can't handle
    creator_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    creator = sa.orm.relationship('User', foreign_keys=[creator_id])
    updater_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    updater = sa.orm.relationship('User', foreign_keys=[updater_id])
    owner_id = sa.Column(sa.Integer)
    owner_type = sa.Column(sa.String)
    owner = sa_utils.generic_relationship(owner_type, owner_id)

class User(BaseModel):
    __tablename__ = 'users'
    __repr_attrs__ = ['user_name']

class Group(BaseModel):
    __tablename__ = 'groups'
    __repr_attrs__ = ['name']

class Click(BaseModel):
    __tablename__ = 'clicks'
    __repr_attrs__ = ['notebook_id', 'user_id', 'action']

Base.prepare(
    nbgdb.engine,
    reflect=True,
    classname_for_table=nbgdb.rails_classname_for_table,
    name_for_collection_relationship=nbgdb.rails_collection_name
)

# Pull the rest of the reflected classes up into this namespace
for cls in Base.classes:
    exec(f"{cls.__name__} = Base.classes.{cls.__name__}")
