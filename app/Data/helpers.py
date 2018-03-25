from app import database as db


def table_name_to_object(sql_table_name):
    meta = db.MetaData(db.engine)
    table = db.Table(sql_table_name, meta, autoload=True)
    return table
