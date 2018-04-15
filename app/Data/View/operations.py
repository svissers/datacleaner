from app import database as db
import pandas as pd
import datetime
from app.Data.models import Dataset
from app.Data.operations import get_dataset_with_id


def get_most_frequent_value(table_name, column):
    return db.engine.execute(
        'SELECT "{0}", COUNT("{0}") AS "frequency" '
        'FROM "{1}" '
        'GROUP BY "{0}" '
        'ORDER BY "frequency" DESC '
        'LIMIT 1;'
        .format(column, table_name)
    ).first()


def get_number_of_null_values(table_name, column, text_type=False):
    if text_type:
        return db.engine.execute(
            'SELECT COUNT(*) '
            'FROM "{1}" '
            'WHERE "{0}" IS NULL OR "{0}" = \'\''
            .format(column, table_name)
        ).first()[0]
    else:
        return db.engine.execute(
            'SELECT COUNT(*) '
            'FROM "{1}" '
            'WHERE "{0}" IS NULL'
            .format(column, table_name)
        ).first()[0]


def get_average_value(table_name, column):
    return str(
        db.engine.execute(
            'SELECT AVG("{0}") '
            'FROM "{1}" '
            .format(column, table_name)
        ).first().avg
    )


def get_maximum_value(table_name, column):
    return db.engine.execute(
        'SELECT "{0}" '
        'FROM "{1}" '
        'WHERE "{0}" IS NOT NULL '
        'ORDER BY "{0}" DESC '
        'LIMIT 1;'
        .format(column, table_name)
    ).first()[0]


def get_minimum_value(table_name, column):
    return db.engine.execute(
        'SELECT "{0}" '
        'FROM "{1}" '
        'WHERE "{0}" IS NOT NULL '
        'ORDER BY "{0}" ASC '
        'LIMIT 1;'
        .format(column, table_name)
    ).first()[0]


def export_csv(table_name, delim=',', quote='"', null=''):
    try:
        df = pd.read_sql_table(table_name, db.engine)
        df = df.drop('index', 1)
        return df.to_csv(sep=delim, quotechar=quote, na_rep=null, index=False)
    except:
        print('AN ERROR OCCURED WHILE EXPORTING TO CSV')


def join_datasets(left_id,
                  left_column,
                  right_id,
                  right_column,
                  join_type,
                  name,
                  desc):
    db_engine = db.engine

    dataset_left = get_dataset_with_id(left_id)
    dataset_right = get_dataset_with_id(right_id)

    dataframe_left = pd.read_sql_table(
        table_name=dataset_left.working_copy,
        con=db_engine,
        index_col='index'
    )
    dataframe_right = pd.read_sql_table(
        table_name=dataset_right.working_copy,
        con=db_engine,
        index_col='index'
    )
    result_dataframe = None

    print(dataframe_left)
    print(dataframe_right)

    suffixes = ('left', 'right')

    if join_type == "cross":
        dataframe_left['temp'] = 0
        dataframe_right['temp'] = 0
        result_dataframe = pd.merge(dataframe_left, dataframe_right, on='temp')
        result_dataframe = result_dataframe.drop(labels=['temp'], axis=1)
    elif join_type == "inner join":
        result_dataframe = pd.merge(
            dataframe_left,
            dataframe_right,
            left_on=left_column,
            right_on=right_column,
            how='inner',
            suffixes=suffixes
        )
    elif join_type == "left outer":
        result_dataframe = pd.merge(
            dataframe_left,
            dataframe_right,
            left_on=left_column,
            right_on=right_column,
            how='left',
            suffixes=suffixes
        )
    elif join_type == "right outer":
        result_dataframe = pd.merge(
            dataframe_left,
            dataframe_right,
            left_on=left_column,
            right_on=right_column,
            how='right',
            suffixes=suffixes
        )
    elif join_type == "full outer":
        result_dataframe = pd.merge(
            dataframe_left,
            dataframe_right,
            left_on=left_column,
            right_on=right_column,
            how='outer',
            suffixes=suffixes
        )

    table_name = str(datetime.datetime.now())
    table_name = table_name.replace(" ", "")
    table_name = table_name.replace("-", "")
    table_name = table_name.replace(":", "")
    table_name = table_name.replace(".", "")
    original = "og" + table_name
    working_copy = "wc" + table_name

    result_dataframe.to_sql(name=original, con=db_engine, if_exists="fail")
    result_dataframe.to_sql(name=working_copy, con=db_engine, if_exists="fail")

    new_dataset = Dataset(
        name,
        original,
        working_copy,
        desc,
        dataset_left.project.id
    )
    db.session.add(new_dataset)
    db.session.commit()