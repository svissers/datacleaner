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
            elif str(column.type) == 'TIMESTAMP WITHOUT TIME ZONE':
                col_type = 'TIMESTAMP'
            else:
                col_type = str(column.type)
            columns.append(
                (col_name, col_type)
            )
    return columns


def escape_quotes(string):
    return_string = ''
    for c in string:
        if c == '\'':
            return_string += '\''
        elif c == '"':
            return_string += '\"'
        return_string += c
    return return_string
