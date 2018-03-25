from app import database as db


def change_column_type(table_name, table_col, new_type):
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