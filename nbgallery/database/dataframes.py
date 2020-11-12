"""
Commonly used nbgallery datasets as pandas dataframes.
"""

import pandas as pd
import sqlalchemy as sa

import nbgallery.database as db
import nbgallery.database.orm as orm

# Note: we're using "classic" SQLAlchemy instead of ORM here since we don't
# need objects to be created for each row.
#
# https://docs.sqlalchemy.org/en/13/core/tutorial.html

# For debugging, you can print() the select object right before the read_sql()
# call to see the SQL text.

def notebooks():
    """
    Dataframe of metadata for all notebooks
    """
    return pd.read_sql_table(orm.Notebook.__tablename__, db.engine)

def notebooks_with_summaries():
    """
    Dataframe of notebook metadata joined with summary stats
    """
    nb = orm.Notebook.__table__
    nbs = orm.NotebookSummary.__table__
    nbs_columns = list(nbs.columns)
    nbs_columns.remove(nbs.c.id)
    nbs_columns.remove(nbs.c.notebook_id)
    nbs_columns.remove(nbs.c.created_at)
    nbs_columns.remove(nbs.c.updated_at)
    s = sa.select([nb] + nbs_columns).select_from(nb.join(nbs))
    return pd.read_sql(s, db.engine)

def user_select_columns():
    """
    Useful columns from the users table, omitting authentication-related
    columns like password.
    """
    u = orm.User.__table__
    return [
        u.c.id,
        u.c.user_name,
        u.c.email,
        u.c.first_name,
        u.c.last_name,
        u.c.org,
        u.c.created_at,
        u.c.updated_at,
        u.c.sign_in_count,
        u.c.last_sign_in_at
    ]

def users():
    """
    Dataframe of metadata for all users
    """
    s = sa.select(user_select_columns())
    return pd.read_sql(s, db.engine)

def users_with_summaries():
    """
    Dataframe of user metadata joined with summary stats
    """
    u = orm.User.__table__
    us = orm.UserSummary.__table__
    us_columns = list(us.columns)
    us_columns.remove(us.c.id)
    us_columns.remove(us.c.user_id)
    us_columns.remove(us.c.created_at)
    us_columns.remove(us.c.updated_at)
    s = sa.select(user_select_columns() + us_columns).\
        select_from(u.join(us))
    return pd.read_sql(s, db.engine)

def click_default_actions():
    """
    The click actions we're usually most interested in -- direct actions by a
    user on a notebook like view, execute, etc.
    """
    return [
        'created notebook',
        'edited notebook',
        'viewed notebook',
        'ran notebook',
        'executed notebook'
    ]

def add_click_filters(select, min_date=None, max_date=None, user_id=None, notebook_id=None, actions=None):
    """
    Add SQL filters for click queries
    """
    t = orm.Click.__table__
    if min_date:
        select = select.where(t.c.created_at >= min_date)
    if max_date:
        select = select.where(t.c.created_at <= max_date)
    if user_id:
        select = select.where(t.c.user_id == user_id)
    if notebook_id:
        select = select.where(t.c.notebook_id == notebook_id)
    if actions:
        select = select.where(t.c.action.in_(actions))
    else:
        select = select.where(t.c.action.in_(click_default_actions()))
    return select

def clicks(min_date=None, max_date=None, user_id=None, notebook_id=None, actions=None):
    """
    Dataframe with one row per click (user-notebook interaction).  Warning:
    could be large!
    """
    t = orm.Click.__table__
    s = sa.select([
        t.c.user_id,
        t.c.notebook_id,
        t.c.action,
        t.c.created_at.label('timestamp')
    ])
    s = add_click_filters(s, min_date=min_date, max_date=max_date, user_id=user_id, notebook_id=notebook_id, actions=actions)
    return pd.read_sql(s, db.engine)

def clicks_rollup(min_date=None, max_date=None, user_id=None, notebook_id=None, actions=None):
    """
    Dataframe with one row per (user, notebook, action) tuple, with count and
    first/last timestamp
    """
    t = orm.Click.__table__
    s = sa.select([
        t.c.user_id,
        t.c.notebook_id,
        t.c.action,
        sa.func.count(t.c.id).label('count'),
        sa.func.min(t.c.created_at).label('first'),
        sa.func.max(t.c.created_at).label('last')
    ]).group_by(t.c.user_id, t.c.notebook_id, t.c.action)
    s = add_click_filters(s, min_date=min_date, max_date=max_date, user_id=user_id, notebook_id=notebook_id, actions=actions)
    return pd.read_sql(s, db.engine)

def clicks_rollup_pivot(min_date=None, max_date=None, user_id=None, notebook_id=None):
    """
    Dataframe with one row per (user, notebook) tuple, with action counts and
    first/last timestamp
    """
    t = orm.Click.__table__
    columns = [t.c.user_id, t.c.notebook_id, sa.func.count(t.c.id).label('count')]
    columns += [
        sa.text(f"COUNT(CASE WHEN action='{action}' THEN 1 END) AS {action.split()[0]}")
        for action in click_default_actions()
    ]
    columns += [
        sa.func.min(t.c.created_at).label('first'),
        sa.func.max(t.c.created_at).label('last')
    ]
    s = sa.select(columns).group_by(t.c.user_id, t.c.notebook_id)
    s = add_click_filters(s, min_date=min_date, max_date=max_date, user_id=user_id, notebook_id=notebook_id)
    return pd.read_sql(s, db.engine)
