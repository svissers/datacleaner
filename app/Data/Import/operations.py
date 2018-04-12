from app.Data.models import Dataset
from app import database
import pandas
import datetime
from app.Data.operations import get_dataset_with_id


def upload_csv(name, description, file, project):
    db_engine = database.engine
    csv_dataframe = pandas.read_csv(file)

    table_name = str(datetime.datetime.now())
    table_name = table_name.replace(" ", "")
    table_name = table_name.replace("-", "")
    table_name = table_name.replace(":", "")
    table_name = table_name.replace(".", "")
    original = "og" + table_name
    working_copy = "wc" + table_name

    csv_dataframe.to_sql(name=original, con=db_engine, if_exists="fail")
    csv_dataframe.to_sql(name=working_copy, con=db_engine, if_exists="fail")

    new_dataset = Dataset(name, original, working_copy, description, project)
    database.session.add(new_dataset)
    database.session.commit()


def update_dataset_with_id(dataset_id, new_name, new_description):
    dataset = get_dataset_with_id(dataset_id)
    if dataset is None:
        raise RuntimeError('No dataset associated with this id.')
    else:
        dataset.name = new_name
        dataset.description = new_description
        database.session.commit()


def delete_dataset_with_id(dataset_id):
    dataset = get_dataset_with_id(dataset_id)
    if dataset is None:
        raise RuntimeError('No dataset associated with this id.')
    else:
        database.engine.execute(
            'DROP TABLE {0}'.format(dataset.working_copy)
        )
        database.engine.execute(
            'DROP TABLE {0}'.format(dataset.original_data)
        )
        database.session.delete(dataset)
        database.session.commit()


def upload_joined(
        join_type, join_name, join_description,
        left_file, left_column,
        right_file, right_column,
        project_id
):
    db_engine = database.engine
    dataframe_left = pandas.read_csv('./file_queue/' + left_file)
    dataframe_right = pandas.read_csv('./file_queue/' + right_file)
    result_dataframe = pandas.DataFrame()

    suffixes = ('left', 'right')

    if join_type == "cross join":
        dataframe_left['temp'] = 0
        dataframe_right['temp'] = 0
        result_dataframe = pandas.merge(dataframe_left, dataframe_right, on='temp')
        result_dataframe = result_dataframe.drop(labels=['temp'], axis=1)
    elif join_type == "inner join":
        result_dataframe = pandas.merge(
            dataframe_left,
            dataframe_right,
            left_on=left_column,
            right_on=right_column,
            how='inner',
            suffixes=suffixes
        )
    elif join_type == "left outer join":
        result_dataframe = pandas.merge(
            dataframe_left,
            dataframe_right,
            left_on=left_column,
            right_on=right_column,
            how='left',
            suffixes=suffixes
        )
    elif join_type == "right outer join":
        result_dataframe = pandas.merge(
            dataframe_left,
            dataframe_right,
            left_on=left_column,
            right_on=right_column,
            how='right',
            suffixes=suffixes
        )
    elif join_type == "full outer join":
        result_dataframe = pandas.merge(
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
        join_name,
        original,
        working_copy,
        join_description,
        project_id
    )
    database.session.add(new_dataset)
    database.session.commit()

