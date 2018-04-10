from app import database as db
import pandas as pd
import re


def restore_original(table_name):
    """
    Resets given table to its original state
    :param table_name: name of the the table to be reset
    """
    try:
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
    except:
        print("FAILED TO RESTORE ORIGINAL")


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
            'TYPE INTEGER USING "{1}"::integer'
            .format(table_name, table_col))
    if new_type == 'BIGINT':
        db.engine.execute(
            'ALTER TABLE {0} '
            'ALTER COLUMN "{1}" '
            'TYPE BIGINT USING "{1}"::bigint'
            .format(table_name, table_col))
    if new_type == 'DOUBLE PRECISION':
        db.engine.execute(
            'ALTER TABLE {0} '
            'ALTER COLUMN "{1}" '
            'TYPE DOUBLE PRECISION USING "{1}"::double precision'
            .format(table_name, table_col))
    if new_type in ['VARCHAR(10)', 'VARCHAR(25)', 'VARCHAR(255)']:
        length = 255
        if new_type == 'VARCHAR(10)':
            length = 10
        elif new_type == 'VARCHAR(25)':
            length = 25
        elif new_type == 'VARCHAR(255)':
            length = 255
        if current_type == 'date':
            db.engine.execute(
                'ALTER TABLE {0} '
                'ALTER COLUMN "{1}" '
                'TYPE VARCHAR({2}) USING to_char("{1}", \'DD/MM/YYYY\')'
                .format(table_name, table_col, length))
        elif current_type == 'timestamp with time zone':
            db.engine.execute(
                'ALTER TABLE {0} '
                'ALTER COLUMN "{1}" '
                'TYPE VARCHAR({2}) '
                'USING to_char("{1}", \'DD/MM/YYYY HH24:MI:SS\')'
                .format(table_name, table_col, length))
        else:
            db.engine.execute(
                'ALTER TABLE {0} '
                'ALTER COLUMN "{1}" '
                'TYPE VARCHAR({2})'
                .format(table_name, table_col, length))
    if new_type == 'TEXT':
        if current_type == 'date':
            db.engine.execute(
                'ALTER TABLE {0} '
                'ALTER COLUMN "{1}" '
                'TYPE TEXT USING to_char("{1}", \'DD/MM/YYYY\')'
                .format(table_name, table_col))
        elif current_type == 'timestamp with time zone':
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
    if new_type == 'BOOLEAN':
        db.engine.execute(
            'ALTER TABLE {0} '
            'ALTER COLUMN "{1}" '
            'TYPE BOOLEAN USING "{1}"::boolean'
            .format(table_name, table_col))
    if new_type == 'DATE':
        if current_type == 'timestamp with time zone':
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
                'TYPE TIMESTAMP WITH TIME ZONE'
                .format(table_name, table_col))
        else:
            db.engine.execute(
                'ALTER TABLE {0} '
                'ALTER COLUMN "{1}" '
                'TYPE TIMESTAMP WITH TIME ZONE '
                'USING to_timestamp("{1}", \'DD/MM/YYYY HH24:MI:SS\')'
                .format(table_name, table_col))


def drop_attribute(table_name, attr):
    """
    Drops given attribute from given table
    :param table_name: table to perform the operation on
    :param attr: attribute to drop
    """
    try:
        db.engine.execute(
            'ALTER TABLE "{0}" DROP COLUMN IF EXISTS "{1}"'.
            format(table_name, attr)
        )
    except:
        print("FAILED TO DROP ATTRIBUTE {0} FROM {1}".format(attr, table_name))


def one_hot_encode(table_name, attr):
    """
    One hot encodes given attribute
    :param table_name: table on which to perform the operation
    :param attr: attribute to one hot encode
    :return:
    """
    try:
        dataframe = pd.read_sql_table(table_name, db.engine)
        one_hot = pd.get_dummies(dataframe[attr])
        dataframe = dataframe.join(one_hot)
        db.engine.execute(
            'DROP TABLE "{0}"'.format(table_name)
        )
        dataframe.to_sql(name=table_name, con=db.engine, if_exists="fail")
    except:
        print('ONE-HOT ENCODING FAILED')


def fill_null_with(table_name, attr, value):
    """
    Fills all NULL values with provided value in table_name.attr
    :param table_name: table to perform the operation on
    :param attr: attribute containing NULL values
    :param value: value to insert
    """
    try:
        db.engine.execute(
            'UPDATE "{0}"'
            'SET "{1}" = {2}'
            'WHERE "{1}" IS NULL'
            .format(table_name, attr, value)
        )
    except:
        print('FILL VALUE FAILED')


def fill_null_with_average(table_name, attr):
    """
    Fills all NULL values with average value in table_name.attr
    :param table_name: table to perform the operation on
    :param attr: attribute containing NULL values
    """
    try:
        dataframe = pd.read_sql_table(table_name, db.engine, columns=[attr])
        average = dataframe[attr].mean()
        db.engine.execute(
            'UPDATE "{0}"'
            'SET "{1}" = {2}'
            'WHERE "{1}" IS NULL'
            .format(table_name, attr, average)
        )
    except:
        print('FILL AVERAGE FAILED')


def fill_null_with_median(table_name, attr):
    """
    Fills all NULL values with median value in table_name.attr
    :param table_name: table to perform the operation on
    :param attr: attribute containing NULL values
    """
    try:
        dataframe = pd.read_sql_table(table_name, db.engine, columns=[attr])
        median = dataframe[attr].median()
        db.engine.execute(
            'UPDATE "{0}"'
            'SET "{1}" = {2}'
            'WHERE "{1}" IS NULL'
            .format(table_name, attr, median)
        )
    except:
        print('FILL MEAN FAILED')


def non_text_find_replace(table_name, attr, find, replace):
    """
    Find and replace function for non-text values where case doesn't matter
    :param table_name: table to perform the operation on
    :param attr: attribute to search
    :param find: value to replace
    :param replace: replacement value
    """
    try:
        db.engine.execute(
            'UPDATE "{0}"'
            'SET "{1}" = {2}'
            'WHERE "{1}" = {3}'
            .format(table_name, attr, replace, find)
        )
    except:
        print('NON-TEXT FIND-REPLACE FAILED')


def text_find_replace(table_name, attr, find, replace, ignore_case=False):
    """
    Find and replace function for text values where case matters
    :param table_name: table to perform the operation on
    :param attr: attribute to search
    :param find: value to replace
    :param replace: replacement value
    :param ignore_case: bool indicating case sensitivity
    """
    try:
        if ignore_case:
            db.engine.execute(
                'UPDATE "{0}"'
                'SET "{1}" = \'{2}\''
                'WHERE LOWER("{1}") = LOWER(\'{3}\')'
                .format(table_name, attr, replace, find)
            )
        else:
            db.engine.execute(
                'UPDATE "{0}"'
                'SET "{1}" = \'{2}\''
                'WHERE "{1}" = \'{3}\''
                .format(table_name, attr, replace, find)
            )
    except:
        print('TEXT FIND-REPLACE FAILED')


def text_regex_find_replace(table_name, attr, regex, replace):
    """
    Find and replace function for text values using a regex for lookup
    :param table_name: table to perform the operation on
    :param attr: attribute to search
    :param regex: regex used for lookup
    :param replace: replacement value
    """
    try:
        is_valid = True
        try:
            re.compile(regex)
        except re.error:
            is_valid = False
        if is_valid:
            db.engine.execute(
                'UPDATE "{0}"'
                'SET "{1}" = REGEXP_REPLACE("{1}", \'{2}\', {3})'
                .format(table_name, attr, regex, replace)
            )
    except:
        print('TEXT REGEX FIND-REPLACE FAILED')


def normalize_attribute(table_name, attr):
    """
    Normalizes table_name.attr using z-score method
    :param table_name: table to perform the operation on
    :param attr: attribute to normalize
    """
    try:
        df = pd.read_sql_table(table_name, db.engine)
        df[attr] = (df[attr] - df[attr].mean()) / df[attr].std(ddof=0)
        db.engine.execute(
            'DROP TABLE "{0}"'.format(table_name)
        )
        df.to_sql(name=table_name, con=db.engine, if_exists="fail")
    except:
        print('NORMALIZATION FAILED')


def remove_outliers(table_name, attr, value, smaller_than=False):
    """
    Removes outliers based on provided value
    :param table_name: table to perform the operation on
    :param attr: attribute to search for outliers
    :param value: extrema value
    :param smaller_than:  if true values smaller than are filtered,
                          values greater than otherwise
    """
    try:
        if smaller_than:
            db.engine.execute(
                'DELETE FROM "{0}"'
                'WHERE "{1}" < {2}'
                .format(table_name, attr, value)
            )
        else:  # greater than
            db.engine.execute(
                'DELETE FROM "{0}"'
                'WHERE "{1}" > {2}'
                .format(table_name, attr, value)
            )
    except:
        print('REMOVE OUTLIERS FAILED')


def delete_rows(table_name, column, operator, condition):
    if operator == '=':
        db.engine.execute(
            'DELETE FROM "{0}" '
            'WHERE "{1}"=\'{2}\''
            .format(table_name, column, condition)
        )
    elif operator == '<':
        remove_outliers(table_name, column, condition, True)
    elif operator == '>':
        remove_outliers(table_name, column, condition, False)
    elif operator == 'CONTAINS':
        db.engine.execute(
            'DELETE FROM "{0}" '
            'WHERE "{1}" ~ \'{2}\''
            .format(table_name, column, condition)
        )


def discretize_width(table_name, attr, intervals, dataframe=None):
    """
    Discretizes table_name.attr into a number of equal-width
    intervals equal to interval amount
    :param table_name: table to perform operation on
    :param attr: attribute to discretize
    :param intervals:
        - int: number of equal width intervals
        - [int]: non-uniform interval edges
    :param dataframe: Dataframe if data has already been read from sql
    """
    try:
        if dataframe is not None:
            df = dataframe
        else:
            df = pd.read_sql_table(table_name, db.engine)
        if isinstance(intervals, list):
            column_name = attr + '_custom_intervals'
        else:
            column_name = attr + '_' + intervals + '_eq_intervals'
        df[column_name] = pd.cut(df[attr], intervals)
        db.engine.execute(
            'DROP TABLE "{0}"'.format(table_name)
        )
        df.to_sql(name=table_name, con=db.engine, if_exists="fail")
    except:
        print('WIDTH DISCRETIZATION FAILED')


def discretize_eq_freq(table_name, attr, intervals):
    """
    Discretizes table_name.attr into a number of equal-frequency
    intervals equal to intervals
    :param table_name: table to perform operation on
    :param attr: attribute to discretize
    :param intervals: number of equal frequency intervals
    """
    try:
        df = pd.read_sql_table(table_name, db.engine)
        attr_length = len(df[attr])
        elements_per_interval = attr_length//intervals
        sorted_data = list(df[attr].sort_values())
        selector = 0
        edge_list = []
        while selector < attr_length:
            edge_list.append(sorted_data[selector])
            selector = selector + elements_per_interval
        if edge_list[-1] != sorted_data[-1]:
            edge_list.append(sorted_data[-1])
        # Extend outer edges with 0.1% to include min and max values
        edge_list[0] = edge_list[0]-edge_list[0]*0.001
        edge_list[-1] = edge_list[-1]+edge_list[-1]*0.001

        discretize_width(table_name, attr, edge_list)
    except:
        print('EQUAL FREQUENCY DISCRETIZATION FAILED')
