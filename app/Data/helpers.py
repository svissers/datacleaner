from app import database as db
import re
import datetime

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

def extract_tables_from_dump(file):
    tables = []
    tables = re.findall(r"CREATE(?: TEMPORARY)? TABLE(?: IF(?: NOT)? EXISTS)? ([^\s]*) ?\(", file, re.IGNORECASE)
    tables = list(set(re.findall(r"INSERT INTO ([^\s]*) ", file, re.IGNORECASE) + tables))
    tabledict = {}
    table_name = str(datetime.datetime.now())
    table_name = table_name.replace(" ", "")
    table_name = table_name.replace("-", "")
    table_name = table_name.replace(":", "")
    table_name = table_name.replace(".", "")
    table_name = "og" + table_name + "_"
    for index in range(len(tables)):
        tabledict[tables[index]] = table_name+str(index)
    return tabledict

def escape_quotes(string):
    return_string = ''
    for c in string:
        if c == '\'':
            return_string += '\''
        elif c == '"':
            return_string += '\"'
        return_string += c
    return return_string
