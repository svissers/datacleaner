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
            col_type = ''
            if str(column.type) == 'BIGINT':
                col_type = 'INTEGER'
            elif str(column.type) == 'DOUBLE PRECISION':
                col_type = 'DOUBLE'
            else:
                col_type = str(column.type)
            columns.append(
                (col_name, col_type)
            )
    return columns
