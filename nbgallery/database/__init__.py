import re

import inflect
import sqlalchemy as sa
import sqlalchemy.orm

from nbgallery.config import mysql_url

# Database connection
engine = sa.create_engine(mysql_url)

# Session class for ORM usage
Session = sqlalchemy.orm.sessionmaker(bind=engine)

# For singular/plural conversions, etc.
inflector = inflect.engine()

def camelize(s):
    """ Convert underscores to camelcase; e.g. foo_bar => FooBar """
    return s[0].upper() + re.sub(r'_([a-z])', lambda m: m.group(1).upper(), s[1:])
    
def uncamelize(s):
    """ Convert camelcase to underscores; e.g. FooBar => foo_bar """
    return s[0].lower() + re.sub(r'[A-Z]', lambda m: "_%s" % m.group(0).lower(), s[1:])

def rails_classname_for_table(base, tablename, table):
    """
    Returns Rails conventional class name for a given table.
    The table name is camelized and depluralized; e.g. table_names => TableName
    """
    return camelize(inflector.singular_noun(tablename))

def rails_collection_name(base, local_cls, referred_cls, constraint):
    """
    Returns Rails conventional collection name for non-scalar relationship.
    The class name is decamelized and pluralized; e.g ClassName => class_names
    """
    referred_name = referred_cls.__name__
    return inflector.plural_noun(uncamelize(referred_name))

