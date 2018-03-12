from app._data.models import ProjectAccess, Project, Dataset, View, Action, db
import pandas as pd
import datetime


def create_project(project_name, description, user_id):
    new_project = Project(project_name, description)
    db.session.add(new_project)
    db.session.commit()
    new_access = ProjectAccess(user_id, new_project.id)
    db.session.add(new_access)
    db.session.commit()


def get_projects(user_id, description=False):
    query_data = db.session.query(Project).\
        join(ProjectAccess, Project.id == ProjectAccess.project_id).\
        filter(ProjectAccess.user_id == user_id)
    if description:
        return [(p.id, p.name, p.description) for p in query_data]
    return [(p.id, p.name) for p in query_data]


def get_tables(user_id, project_id=None):
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


def upload_csv(name, description, file, project):
    db_engine = db.engine
    csv_dataframe = pd.read_csv(file)

    table_name = str(datetime.datetime.now())
    table_name = table_name.replace(" ", "")
    table_name = table_name.replace("-", "")
    table_name = table_name.replace(":", "")
    table_name = table_name.replace(".", "")
    table_name = "t" + table_name

    print(table_name)

    csv_dataframe.to_sql(name=table_name, con=db_engine, if_exists="fail")

    new_set = Dataset(name, table_name, description, project)
    db.session.add(new_set)
    db.session.commit()


def upload_zip(name, description, file, project):
    pass


def upload_dump(name, description, file, project):
    pass