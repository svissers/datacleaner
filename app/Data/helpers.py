from app import database as db


def table_name_to_object(sql_table_name):
    meta = db.MetaData(db.engine)
    table = db.Table(sql_table_name, meta, autoload=True)
    return table


def extract_columns_from_db(table):
    columns = []
    for column in table.columns:
        start = str(column).find('.') + 1
        col_name = str(column)[start:]
        if col_name != 'index':
            columns.append(
                (col_name, str(column.type))
            )
    return columns
