from app.Data.models import Dataset
from app.Project.models import Project, Access
from app import database as db


def get_datasets(user_id, project_id=None):
    query_data = db.session.query(Dataset).\
        join(Project, Project.id == Dataset.project_id).\
        join(Access, Project.id == Access.project_id).\
        filter(Access.user_id == user_id)
    if project_id is not None:
        query_data = query_data.filter(Project.id == project_id)

    return query_data