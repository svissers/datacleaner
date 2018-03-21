from app._data.models import ProjectAccess, Project, Dataset, View, Action, db
import pandas as pd
import datetime


def create_project(project_name, description, user_id):
    new_project = Project(project_name, description)
    new_project.add_to_database()
    ProjectAccess(user_id, new_project.id, owner=True).add_to_database()


def share_project_with(project_id, user_id):
    ProjectAccess(user_id, project_id, owner=False).add_to_database()


def get_projects(user_id, description=False):
    query_data = db.session.query(Project).\
        join(ProjectAccess, Project.id == ProjectAccess.project_id).\
        filter(ProjectAccess.user_id == user_id)
    if description:
        return [(p.id, p.name, p.description) for p in query_data]
    return [(p.id, p.name) for p in query_data]


def get_datasets(user_id, project_id=None):
    query_data = db.session.query(Dataset).\
        join(Project, Project.id == Dataset.project_id).\
        join(ProjectAccess, Project.id == ProjectAccess.project_id).\
        filter(ProjectAccess.user_id == user_id)

    if project_id is not None:
        query_data = query_data.filter(Project.id == project_id)

    return [
        (t.id, t.name, t.description, t.sql_table_name, t.project_id)
        for t in query_data
    ]


def table_name_to_object(sql_table_name):
    meta = db.MetaData(db.engine)
    table = db.Table(sql_table_name, meta, autoload=True)
    return table


def upload_csv(name, description, file, project):
    db_engine = db.engine
    csv_dataframe = pd.read_csv(file)

    table_name = str(datetime.datetime.now())
    table_name = table_name.replace(" ", "")
    table_name = table_name.replace("-", "")
    table_name = table_name.replace(":", "")
    table_name = table_name.replace(".", "")
    table_name = "t" + table_name

    csv_dataframe.to_sql(name=table_name, con=db_engine, if_exists="fail")

    Dataset(name, table_name, description, project).add_to_database()


def upload_join(name, description, file_left, file_right,
                column_left, column_right, join_type, project):
    # ./file_queue
    db_engine = db.engine
    dataframe_left = pd.read_csv('./file_queue/' + file_left)
    dataframe_right = pd.read_csv('./file_queue/' + file_right)
    result_dataframe = pd.DataFrame()
    if join_type == "CROSS JOIN":
        dataframe_left['temp'] = 0
        dataframe_right['temp'] = 0
        result_dataframe = pd.merge(dataframe_left, dataframe_right, on='temp')
        result_dataframe = result_dataframe.drop(labels=['temp'], axis=1)
    elif join_type == "INNER JOIN":
        result_dataframe = pd.merge(
            dataframe_left,
            dataframe_right,
            left_on=column_left,
            right_on=column_right,
            how='inner'
        )
    elif join_type == "LEFT OUTER JOIN":
        result_dataframe = pd.merge(
            dataframe_left,
            dataframe_right,
            left_on=column_left,
            right_on=column_right,
            how='left'
        )
    elif join_type == "RIGHT OUTER JOIN":
        result_dataframe = pd.merge(
            dataframe_left,
            dataframe_right,
            left_on=column_left,
            right_on=column_right,
            how='right'
        )
    elif join_type == "FULL OUTER JOIN":
        result_dataframe = pd.merge(
            dataframe_left,
            dataframe_right,
            left_on=column_left,
            right_on=column_right,
            how='outer'
        )

    table_name = str(datetime.datetime.now())
    table_name = table_name.replace(" ", "")
    table_name = table_name.replace("-", "")
    table_name = table_name.replace(":", "")
    table_name = table_name.replace(".", "")
    table_name = "t" + table_name

    result_dataframe.to_sql(name=table_name, con=db_engine, if_exists="fail")

    Dataset(name, table_name, description, project).add_to_database()


def upload_dump(name, description, file, project):
    pass
