from app import database as db
import pandas as pd
import datetime
from app.Data.models import Dataset
from app.Data.operations import get_dataset_with_id


def export_csv(table_name, delim=',', quote='"', null=''):
    try:
        df = pd.read_sql_table(table_name, db.engine)
        df.drop(labels='index')
        df.fillna(null)
        return df.to_csv(sep=delim, quotechar=quote)
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