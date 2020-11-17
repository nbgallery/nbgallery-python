"""
Commonly used nbgallery datasets as pandas dataframes.
"""

import datetime

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

def add_date_filters(select, column, min_date=None, max_date=None, days_ago=None):
    """
    Add date filters for click queries.  Specify min_date and/or max_date, or
    specify days_ago to determine min_date based on the current date.  The
    column parameter should be an SQLAlchemy column object; for example
    table.c.created_at.
    """
    if days_ago:
        min_date = datetime.datetime.today().date() - datetime.timedelta(days=days_ago)
        max_date = None
    if min_date:
        select = select.where(column >= min_date)
    if max_date:
        select = select.where(column <= max_date)
    return select

def isiterable(obj):
    """
    Return whether an object is iterable
    """
    # see https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable
    try:
        iter(obj)
        return True
    except:
        return False

def add_id_filter(select, column, ids):
    """
    Add a filter to a query for one or more ids.  If ids is a single value,
    an == clause will be added; if ids is iterable, an IN clause will be
    added. The column parameter should be an SQLAlchemy column object; for
    example table.c.notebook_id.
    """
    if ids is None:
        return select
    elif isiterable(ids):
        return select.where(column.in_(ids))
    else:
        return select.where(column == ids)

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
        'downloaded notebook',
        'ran notebook',
        'executed notebook'
    ]

def add_click_filters(select, min_date=None, max_date=None, days_ago=None, user_id=None, notebook_id=None, actions=None):
    """
    Add SQL filters for click queries
    """
    t = orm.Click.__table__
    select = add_date_filters(select, t.c.created_at, min_date=min_date, max_date=max_date, days_ago=days_ago)
    select = add_id_filter(select, t.c.user_id, user_id)
    select = add_id_filter(select, t.c.notebook_id, notebook_id)
    if actions:
        select = select.where(t.c.action.in_(actions))
    else:
        select = select.where(t.c.action.in_(click_default_actions()))
    return select

def clicks(min_date=None, max_date=None, days_ago=None, user_id=None, notebook_id=None, actions=None):
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
    s = add_click_filters(s, min_date=min_date, max_date=max_date, days_ago=days_ago, user_id=user_id, notebook_id=notebook_id, actions=actions)
    return pd.read_sql(s, db.engine)

def clicks_rollup(min_date=None, max_date=None, days_ago=None, user_id=None, notebook_id=None, actions=None):
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
    s = add_click_filters(s, min_date=min_date, max_date=max_date, days_ago=days_ago, user_id=user_id, notebook_id=notebook_id, actions=actions)
    return pd.read_sql(s, db.engine)

def clicks_rollup_pivot(min_date=None, max_date=None, days_ago=None, user_id=None, notebook_id=None):
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
    s = add_click_filters(s, min_date=min_date, max_date=max_date, days_ago=days_ago, user_id=user_id, notebook_id=notebook_id)
    return pd.read_sql(s, db.engine)

def notebook_clicks_rollup(min_date=None, max_date=None, days_ago=None, notebook_id=None):
    """
    Dataframe with one row per notebook, with action/user counts and first/last
    timestamp.  This contains some of the basic counts currently in the
    notebook_summaries table.
    """
    t = orm.Click.__table__
    columns = [t.c.notebook_id, sa.func.count(t.c.id).label('count')]
    for action in click_default_actions():
        columns.append(sa.text(f"COUNT(CASE WHEN action='{action}' THEN 1 END) AS {action.split()[0]}"))
        columns.append(sa.text(f"COUNT(DISTINCT(CASE WHEN action='{action}' THEN user_id END)) AS users_{action.split()[0]}"))
    columns += [
        sa.func.min(t.c.created_at).label('first'),
        sa.func.max(t.c.created_at).label('last')
    ]
    s = sa.select(columns).group_by(t.c.notebook_id)
    s = add_click_filters(s, min_date=min_date, max_date=max_date, days_ago=days_ago, notebook_id=notebook_id)
    return pd.read_sql(s, db.engine)

def user_clicks_rollup(min_date=None, max_date=None, days_ago=None, user_id=None):
    """
    Dataframe with one row per user, with action/notebook counts and first/last
    timestamp.  This contains some of the counts that currently feed into the
    user contribution scores in the user_summaries table.
    """
    t = orm.Click.__table__
    columns = [t.c.user_id, sa.func.count(t.c.id).label('count')]
    for action in click_default_actions():
        columns.append(sa.text(f"COUNT(CASE WHEN action='{action}' THEN 1 END) AS {action.split()[0]}"))
        columns.append(sa.text(f"COUNT(DISTINCT(CASE WHEN action='{action}' THEN notebook_id END)) AS notebooks_{action.split()[0]}"))
    columns += [
        sa.func.min(t.c.created_at).label('first'),
        sa.func.max(t.c.created_at).label('last')
    ]
    s = sa.select(columns).group_by(t.c.user_id)
    s = add_click_filters(s, min_date=min_date, max_date=max_date, days_ago=days_ago, user_id=user_id)
    return pd.read_sql(s, db.engine)

def add_execution_filters(select, min_date=None, max_date=None, days_ago=None, user_id=None, notebook_id=None):
    """
    Add SQL filters for execution queries
    """
    executions = orm.Execution.__table__
    code_cells = orm.CodeCell.__table__
    select = add_date_filters(select, executions.c.created_at, min_date=min_date, max_date=max_date, days_ago=days_ago)
    select = add_id_filter(select, executions.c.user_id, user_id)
    select = add_id_filter(select, code_cells.c.notebook_id, notebook_id)
    return select

def executions(min_date=None, max_date=None, days_ago=None, user_id=None, notebook_id=None):
    """
    Dataframe with one row per execution (user-cell execution).  Warning:
    could be large!
    """
    executions = orm.Execution.__table__
    code_cells = orm.CodeCell.__table__
    columns = [
        executions.c.id,
        executions.c.user_id,
        executions.c.code_cell_id,
        code_cells.c.notebook_id,
        code_cells.c.cell_number,
        executions.c.success,
        executions.c.runtime,
        executions.c.created_at.label('timestamp')
    ]
    s = sa.select(columns).select_from(executions.join(code_cells))
    s = add_execution_filters(s, min_date=min_date, max_date=max_date, days_ago=days_ago, user_id=user_id, notebook_id=notebook_id)
    return pd.read_sql(s, db.engine)

def cell_execution_rollup(min_date=None, max_date=None, days_ago=None, user_id=None, notebook_id=None):
    """
    Dataframe containing one row per code cell with execution summary data.
    """
    executions = orm.Execution.__table__
    code_cells = orm.CodeCell.__table__
    columns = [
        executions.c.code_cell_id,
        code_cells.c.notebook_id,
        code_cells.c.cell_number,
        sa.func.count(executions.c.user_id.distinct()).label('users'),
        success := sa.cast(sa.func.sum(executions.c.success), sa.Integer).label('success'),
        count := sa.func.count(1).label('count'),
        (success / count).label('pass_rate'),
        sa.func.min(executions.c.created_at).label('first'),
        sa.func.max(executions.c.created_at).label('last')
    ]
    s = sa.select(columns).select_from(executions.join(code_cells)).group_by(executions.c.code_cell_id)
    s = add_execution_filters(s, min_date=min_date, max_date=max_date, days_ago=days_ago, user_id=user_id, notebook_id=notebook_id)
    return pd.read_sql(s, db.engine)

def notebook_cell_count(label='cell_count'):
    """
    Dataframe with notebook_id and number of code cells per notebook.
    """
    code_cells = orm.CodeCell.__table__
    columns = [
        code_cells.c.notebook_id,
        sa.func.count(code_cells.c.cell_number.distinct()).label(label)
    ]
    s = sa.select(columns).group_by(code_cells.c.notebook_id)
    return pd.read_sql(s, db.engine)

def notebook_execution_rollup(min_date=None, max_date=None, days_ago=None, user_id=None, notebook_id=None):
    """
    Dataframe containing one row per notebook with execution summary data.
    """
    executions = orm.Execution.__table__
    code_cells = orm.CodeCell.__table__
    columns = [
        code_cells.c.notebook_id,
        sa.func.count(executions.c.user_id.distinct()).label('users'),
        sa.func.count(code_cells.c.cell_number.distinct()).label('cells_executed'),
        success := sa.cast(sa.func.sum(executions.c.success), sa.Integer).label('cell_exec_success'),
        total := sa.func.count(1).label('cell_exec_count'),
        (success / total).label('cell_pass_rate'),
        sa.func.min(executions.c.created_at).label('first'),
        sa.func.max(executions.c.created_at).label('last')
    ]
    s = sa.select(columns).select_from(executions.join(code_cells)).group_by(code_cells.c.notebook_id)
    s = add_execution_filters(s, min_date=min_date, max_date=max_date, days_ago=days_ago, user_id=user_id, notebook_id=notebook_id)
    df = pd.read_sql(s, db.engine)

    # Add in total cells per notebook so you can see if some weren't executed
    ncc = notebook_cell_count(label='cells_total')
    df = df.merge(ncc, how='inner', on='notebook_id')
    # Reorder columns
    columns = df.columns.to_list()
    columns.remove('cells_total')
    columns.insert(columns.index('cells_executed') + 1, 'cells_total')
    return df[columns]
