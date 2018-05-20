from app import database as db
import pandas as pd
import re
import numpy as np


def rename_attribute(table_name, column, new_name):
    db.engine.execute(
        'ALTER TABLE {0} '
        'RENAME COLUMN "{1}" TO "{2}"'
        .format(table_name, column, new_name)
    )


def delete_attribute(table_name, column):
    db.engine.execute(
        'ALTER TABLE {0} '
        'DROP COLUMN "{1}"'
        .format(table_name, column)
    )


def restore_original(table_name):
    """
    Resets given table to its original state
    :param table_name: name of the the table to be reset
    """
    # Original tables are prepended with og
    # Thus we replace wc with og and have the name of the table
    # with the original data
    original = 'og' + table_name[2:]
    db.engine.execute(
        'DROP TABLE "{0}"'.format(table_name)
    )
    db.engine.execute(
        'CREATE TABLE "{0}" AS SELECT * FROM "{1}"'
        .format(table_name, original)
    )


def change_attribute_type(table_name, table_col, new_type):
    """
    Changes the type of given attribute in given table to new_type
    :param table_name: table containing the attribute
    :param table_col: attribute to change type of
    :param new_type: new type
    """
    current_type = db.engine.execute(
        'SELECT data_type from information_schema.columns '
        'where table_name = \'{0}\' and column_name = \'{1}\';'
        .format(table_name, table_col)
    ).fetchall()[0][0]
    if new_type == 'INTEGER':
        db.engine.execute(
            'ALTER TABLE {0} '
            'ALTER COLUMN "{1}" '
            'TYPE BIGINT USING "{1}"::bigint'
            .format(table_name, table_col))
    if new_type == 'DOUBLE':
        db.engine.execute(
            'ALTER TABLE {0} '
            'ALTER COLUMN "{1}" '
            'TYPE DOUBLE PRECISION USING "{1}"::double precision'
            .format(table_name, table_col))
    if new_type == 'TEXT':
        if current_type == 'date':
            db.engine.execute(
                'ALTER TABLE {0} '
                'ALTER COLUMN "{1}" '
                'TYPE TEXT USING to_char("{1}", \'DD/MM/YYYY\')'
                .format(table_name, table_col))
        elif current_type == 'timestamp without time zone':
            db.engine.execute(
                'ALTER TABLE {0} '
                'ALTER COLUMN "{1}" '
                'TYPE TEXT USING to_char("{1}", \'DD/MM/YYYY HH24:MI:SS\')'
                .format(table_name, table_col))
        else:
            db.engine.execute(
                'ALTER TABLE {0} '
                'ALTER COLUMN "{1}" '
                'TYPE TEXT'
                .format(table_name, table_col))
    if new_type == 'DATE':
        if current_type == 'timestamp without time zone':
            db.engine.execute(
                'ALTER TABLE {0} '
                'ALTER COLUMN "{1}" '
                'TYPE DATE'
                .format(table_name, table_col))
        else:
            db.engine.execute(
                'ALTER TABLE {0} '
                'ALTER COLUMN "{1}" '
                'TYPE DATE USING to_date("{1}", \'DD/MM/YYYY\')'
                .format(table_name, table_col))
    if new_type == 'TIMESTAMP':
        if current_type == 'date':
            db.engine.execute(
                'ALTER TABLE {0} '
                'ALTER COLUMN "{1}" '
                'TYPE TIMESTAMP '
                .format(table_name, table_col))
        else:
            db.engine.execute(
                'ALTER TABLE {0} '
                'ALTER COLUMN "{1}" '
                'TYPE TIMESTAMP '
                'USING to_timestamp("{1}", \'DD/MM/YYYY HH24:MI:SS\')'
                .format(table_name, table_col))


def drop_attribute(table_name, attr):
    """
    Drops given attribute from given table
    :param table_name: table to perform the operation on
    :param attr: attribute to drop
    """
    db.engine.execute(
        'ALTER TABLE "{0}" DROP COLUMN IF EXISTS "{1}"'.
        format(table_name, attr)
    )


def one_hot_encode(table_name, attr):
    """
    One hot encodes given attribute
    :param table_name: table on which to perform the operation
    :param attr: attribute to one hot encode
    :return:
    """
    df = pd.read_sql_table(table_name, db.engine)
    one_hot = pd.get_dummies(df[attr])
    df = df.join(one_hot)
    df.to_sql(name=table_name, con=db.engine, if_exists="replace", index=False)


def fill_null_with(table_name, attr, value, text_type):
    """
    Fills all NULL values with provided value in table_name.attr
    :param table_name: table to perform the operation on
    :param attr: attribute containing NULL values
    :param text_type: indicates whether column is a text type
    :param value: value to insert
    """
    if text_type:
        db.engine.execute(
            'UPDATE "{0}" '
            'SET "{1}" = \'{2}\' '
            'WHERE ("{1}" = \'\') IS NOT FALSE'
            .format(table_name, attr, value)
        )
    else:
        db.engine.execute(
            'UPDATE "{0}" '
            'SET "{1}" = {2} '
            'WHERE "{1}" IS NULL'
            .format(table_name, attr, value)
        )


def fill_null_with_average(table_name, attr):
    """
    Fills all NULL values with average value in table_name.attr
    :param table_name: table to perform the operation on
    :param attr: attribute containing NULL values
    """
    dataframe = pd.read_sql_table(table_name, db.engine, columns=[attr])
    average = dataframe[attr].mean()
    db.engine.execute(
        'UPDATE "{0}" '
        'SET "{1}" = {2} '
        'WHERE "{1}" IS NULL'
        .format(table_name, attr, average)
    )


def fill_null_with_median(table_name, attr):
    """
    Fills all NULL values with median value in table_name.attr
    :param table_name: table to perform the operation on
    :param attr: attribute containing NULL values
    """
    dataframe = pd.read_sql_table(table_name, db.engine, columns=[attr])
    median = dataframe[attr].median()
    db.engine.execute(
        'UPDATE "{0}" '
        'SET "{1}" = {2} '
        'WHERE "{1}" IS NULL'
        .format(table_name, attr, median)
    )


def find_replace(table_name, attr, find, replace):
    db.engine.execute(
        'UPDATE "{0}" '
        'SET "{1}" = \'{2}\' '
        'WHERE "{1}" = \'{3}\' '
        .format(table_name, attr, replace, find)
    )


def substring_find_replace(table_name, attr, find, replace, full=False):
    if full:
        db.engine.execute(
            'UPDATE "{0}" '
            'SET "{1}" = \'{2}\' '
            'WHERE "{1}" LIKE \'%%{3}%%\' '
            .format(table_name, attr, replace, find)
        )
    else:
        db.engine.execute(
            'UPDATE "{0}" '
            'SET "{1}" = REPLACE("{1}", \'{2}\', \'{3}\')'
            .format(table_name, attr, find, replace)
        )


def regex_find_replace(table_name, attr, regex, replace):
    is_valid = True
    try:
        re.compile(regex)
    except re.error:
        is_valid = False
    if is_valid:
        db.engine.execute(
            'UPDATE "{0}" '
            'SET "{1}" = REGEXP_REPLACE("{1}", \'{2}\', \'{3}\')'
            .format(table_name, attr, regex, replace)
        )


def normalize_attribute(table_name, attr):
    """
    Normalizes table_name.attr using z-score method
    :param table_name: table to perform the operation on
    :param attr: attribute to normalize
    """
    df = pd.read_sql_table(table_name, db.engine)
    df[attr + '_normalized'] = (df[attr] - df[attr].mean()) / df[attr].std(ddof=0)
    df.to_sql(name=table_name, con=db.engine, if_exists="replace", index=False)


def nullify_outliers(table_name, attr, value, operator):
    """
    Removes outliers bases on given value and operator
    :param table_name: table to perform the operation on
    :param attr:
    :param value:
    :param operator:
    :return:
    """

    symbol = str()

    if operator == 'gt':
        symbol = '>'
    elif operator == 'st':
        symbol = '<'
    elif operator == 'egt':
        symbol = '>='
    elif operator == 'est':
        symbol = '<='

    db.engine.execute(
        'UPDATE "{0}" '
        'SET "{1}" = NULL '
        'WHERE "{1}" {3} \'{2}\''
        .format(table_name, attr, value, symbol)
    )


def delete_rows(table_name, condition):

    result = db.engine.execute(
        'DELETE FROM "{0}" WHERE {1}'.format(table_name, condition)
    )
    if result.rowcount == 0:
        return False


def discretize_width(table_name, attr, intervals):
    """
    Discretizes table_name.attr into a number of equal-width
    intervals equal to interval amount
    :param table_name: table to perform operation on
    :param attr: attribute to discretize
    :param intervals:
        - int: number of equal width intervals
        - [int]: non-uniform interval edges
    """
    df = pd.read_sql_table(table_name, db.engine)
    if isinstance(intervals, list):
        column_name = attr + '_custom_intervals'
        df[column_name] = pd.cut(df[attr], intervals).apply(str)
    else:
        column_name = attr + '_' + str(intervals) + '_eq_intervals'
        min_val = df[attr].min()
        max_val = df[attr].max()
        width = (max_val + min_val)/intervals
        edges = list(np.arange(min_val, max_val, width))
        if edges[-1] != float(max_val):
            edges.append(max_val)
        df[column_name] = pd.cut(
                df[attr],
                edges,
                include_lowest=True
        ).apply(str)

    df.to_sql(name=table_name, con=db.engine, if_exists="replace", index=False)


def discretize_eq_freq(table_name, attr, intervals):
    """
    Discretizes table_name.attr into a number of equal-frequency
    intervals equal to intervals
    :param table_name: table to perform operation on
    :param attr: attribute to discretize
    :param intervals: number of equal frequency intervals
    """
    df = pd.read_sql_table(table_name, db.engine)
    attr_length = len(df[attr])
    elements_per_interval = attr_length//intervals
    sorted_data = list(df[attr].sort_values())
    selector = 0
    edge_list = []
    while selector < attr_length:
        try:
            edge_list.append(sorted_data[selector])
            selector += elements_per_interval
        except IndexError:
            pass
    if edge_list[-1] != sorted_data[-1] and len(edge_list) == intervals + 1:
        edge_list[-1] = sorted_data[-1]
    elif edge_list[-1] != sorted_data[-1] and len(edge_list) != intervals + 1:
        edge_list.append(sorted_data[-1])

    # Extend outer edges with 0.1% to include min and max values
    edge_list[0] = edge_list[0]-edge_list[0]*0.001
    edge_list[-1] = edge_list[-1]+edge_list[-1]*0.001

    column_name = attr + '_' + str(intervals) + '_eq_freq_intervals'

    df[column_name] = pd.cut(df[attr], edge_list).apply(str)
    df.to_sql(name=table_name, con=db.engine, if_exists="replace", index=False)


def extract_from_date_time(table_name, attr, element):
    """
    Extracts given element from attr of type timeastamp/date/time
    :param table_name: table to perform operation on
    :param attr: attribute to extract from
    :param element: element to extract
    """
    if element == 'date':
        db.engine.execute(
            'ALTER TABLE IF EXISTS {0} '
            'ADD COLUMN "{1} from {2}" DATE;'
            'UPDATE "{0}" '
            'SET "{1} from {2}" =  "{2}"::timestamp::date;'
            .format(table_name, element, attr)
        )
    elif element == 'time':
        db.engine.execute(
            'ALTER TABLE IF EXISTS {0} '
            'ADD COLUMN "{1} from {2}" TEXT;'
            'UPDATE "{0}" '
            'SET "{1} from {2}" =  "{2}"::timestamp::time;'
            .format(table_name, element, attr,)
        )
    else:
        db.engine.execute(
            'ALTER TABLE IF EXISTS {0} '
            'ADD COLUMN "{1} from {2}" TEXT;'
            'UPDATE "{0}" '
            'SET "{1} from {2}" = EXTRACT({1} FROM "{2}");'
            .format(table_name, element, attr)
        )
