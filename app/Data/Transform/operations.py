from app import database as db
import pandas as pd


def restore_original(table_name):
    try:
        original = 't' + table_name[2:]
        db.engine.execute(
            'DROP TABLE {0}'.format(table_name)
        )
        db.engine.execute(
            'SELECT * INTO {0} from {1}'.format(table_name, original)
        )
    except:
        print("FAILED TO RESTORE ORIGINAL")


def change_attribute_type(table_name, table_col, new_type):
    try:
        if new_type == 'INTEGER':
            db.engine.execute(
                'ALTER TABLE {0} ALTER COLUMN {1} TYPE INTEGER USING {1}::integer'.format(table_name, table_col))
        if new_type == 'BIGINT':
            db.engine.execute(
                'ALTER TABLE {0} ALTER COLUMN {1} TYPE BIGINT USING {1}::bigint'.format(table_name, table_col))
        if new_type == 'VARCHAR(10)':
            db.engine.execute(
                'ALTER TABLE {0} ALTER COLUMN {1} TYPE VARCHAR(10)' .format(table_name, table_col))
        if new_type == 'VARCHAR(25)':
            db.engine.execute(
                'ALTER TABLE {0} ALTER COLUMN {1} TYPE VARCHAR(25)' .format(table_name, table_col))
        if new_type == 'VARCHAR(255)':
            db.engine.execute(
                'ALTER TABLE {0} ALTER COLUMN {1} TYPE VARCHAR(255)' .format(table_name, table_col))
        if new_type == 'TEXT':
            db.engine.execute(
                'ALTER TABLE {0} ALTER COLUMN {1} TYPE TEXT'.format(table_name, table_col))
        if new_type == 'BOOLEAN':
            db.engine.execute(
                'ALTER TABLE {0} ALTER COLUMN {1} TYPE BOOLEAN USING {1}::boolean'.format(table_name, table_col))
        if new_type == 'DATE':
            db.engine.execute(
                "ALTER TABLE {0} ALTER COLUMN {1} TYPE DATE USING to_date({1}, 'YYYY-MM-DD')".format(table_name, table_col))
    except Exception:
        print("ERROR")


def drop_attribute(table_name, attr):
    try:
        db.engine.execute(
            'ALTER TABLE {0} DROP COLUMN IF EXISTS {1}'.
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
            'DROP TABLE {0}'.format(table_name)
        )
        dataframe.to_sql(name=table_name, con=db.engine, if_exists="fail")
    except:
        print('ONE-HOT ENCODING FAILED')
