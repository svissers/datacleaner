from .models import Project, Access
from app.User import get_user_with_id
from app import database


def create_project(project_name, description, user_id):
    """
    Create project with given name and description
    :param project_name: project name
    :param description: project description
    :param user_id: id of the creator
    """
    new_project = Project(project_name, description)
    ownership = Access(owner=True)
    ownership.user = get_user_with_id(user_id)
    new_project.users.append(ownership)
    database.session.commit()


def get_project_with_id(project_id):
    """
    Returns project associated with given id
    :param project_id: id used for lookup
    :return Project: Project associated with id
    """
    return Project.query.filter_by(id=project_id).first()


def get_all_projects_for_user(user_id):
    """
    Returns a list of all projects the user with given user_id has access to
    :param user_id: id user for lookup
    :return list(Project): list of Projects
    """
    user = get_user_with_id(user_id)
    return [access.project for access in user.projects]


def share_project(project_id, with_user_id, with_ownership):
    """
    Shares project associated with given project_id with user with given
    user_id, with(out) ownership
    :param project_id: id of project to be shared
    :param with_user_id: id of user to share with
    :param with_ownership: bool indicating whether ownership should be granted
    :exception RuntimeError: thrown if project already shared with user
    """
    project = get_project_with_id(project_id)
    for access in project.users:
        if access.user_id == with_user_id:
            raise RuntimeError(
                'This user already has access to this project.')
    ownership = Access(owner=with_ownership)
    ownership.user = get_user_with_id(with_user_id)
    project.users.append(ownership)
    database.session.commit()
