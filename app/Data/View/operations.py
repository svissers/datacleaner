from app import database as db
import pandas as pd


def export_csv(table_name, delim=',', quote='"', null=''):
    try:
        df = pd.read_sql_table(table_name, db.engine)
        df.drop(labels='index')
        df.fillna(null)
        return df.to_csv(sep=delim, quotechar=quote)
    except:
        print('AN ERROR OCCURED WHILE EXPORTING TO CSV')