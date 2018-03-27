from app import database as db
import pandas as pd


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
            'SELECT * INTO "{0}" from "{1}"'.format(table_name, original)
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
    try:
        current_type = db.engine.execute(
            'SELECT data_type from information_schema.columns '
            'where table_name = \'{0}\' and column_name = \'{1}\';'.format(table_name, table_col)
        ).fetchall()[0][0]
        if new_type == 'INTEGER':
            db.engine.execute(
                'ALTER TABLE {0} ALTER COLUMN "{1}" TYPE INTEGER USING "{1}"::integer'.format(table_name, table_col))
        if new_type == 'BIGINT':
            db.engine.execute(
                'ALTER TABLE {0} ALTER COLUMN "{1}" TYPE BIGINT USING "{1}"::bigint'.format(table_name, table_col))
        if new_type in ['VARCHAR(10)', 'VARCHAR(25)', 'VARCHAR(255)']:
            length = None
            if new_type == 'VARCHAR(10)':
                length = 10
            elif new_type == 'VARCHAR(25)':
                length = 25
            elif new_type == 'VARCHAR(255)':
                length = 255
            if current_type == 'date':
                db.engine.execute(
                    'ALTER TABLE {0} ALTER COLUMN "{1}" TYPE VARCHAR({2}) USING to_char("{1}", \'DD/MM/YYYY\')'.
                    format(table_name, table_col, length))
            else:
                db.engine.execute(
                    'ALTER TABLE {0} ALTER COLUMN "{1}" TYPE VARCHAR({2})'.format(table_name, table_col, length))
        if new_type == 'TEXT':
            if current_type == 'date':
                db.engine.execute(
                    'ALTER TABLE {0} ALTER COLUMN "{1}" TYPE TEXT USING to_char("{1}", \'DD/MM/YYYY\')'.
                    format(table_name, table_col))
            else:
                db.engine.execute(
                    'ALTER TABLE {0} ALTER COLUMN "{1}" TYPE TEXT'.format(table_name, table_col))
        if new_type == 'BOOLEAN':
            db.engine.execute(
                'ALTER TABLE {0} ALTER COLUMN "{1}" TYPE BOOLEAN USING "{1}"::boolean'.format(table_name, table_col))
        if new_type == 'DATE':
            db.engine.execute(
                'ALTER TABLE {0} ALTER COLUMN "{1}" TYPE DATE USING to_date("{1}", \'DD/MM/YYYY\')'.
                format(table_name, table_col))
    except Exception as error:
        print(str(error))


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


def one_hot_encode(table_name, attributes):
    try:
        dataframe = pd.read_sql_table(table_name, db.engine)
        for attr in attributes:
            one_hot = pd.get_dummies(dataframe[attr])
            dataframe = dataframe.drop(attr, axis=1)
            dataframe = dataframe.join(one_hot)
        db.engine.execute(
            'DROP TABLE "{0}"'.format(table_name)
        )
        dataframe.to_sql(name=table_name, con=db.engine, if_exists="fail")
    except:
        print('ONE-HOT ENCODING FAILED')


def fill_null_with(table_name, attribute, value):
    try:
        db.engine.execute(
            'UPDATE "{0}"'
            'SET "{1}" = {2}'
            'WHERE "{1}" IS NULL'
            .format(table_name, attribute, value)
        )
    except:
        print('FILL VALUE FAILED')


def fill_null_with_average(table_name, attr):
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


def text_regex_find_replace(table_name, attr, find, replace):
    try:
        pass
    except:
        print('TEXT REGEX FIND-REPLACE FAILED')
