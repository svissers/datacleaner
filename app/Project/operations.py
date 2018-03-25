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


def cleanup(project_id):
    """
    Cleanup function for projects
    Needed because cleanup needs to happen based on ownership which can't be
    done directly via SQL
    :param project_id: candidate project for cleanup
    """
    accesses = Access.query.filter(Access.project_id == project_id)
    if accesses is None:
        return
    for access in accesses:
        if access.owner:
            return
    project = get_project_with_id(project_id)
    database.session.delete(project)
    database.session.commit()


def delete_project_with_id(project_id, user_id):
    """
    Deletes the project associated with
    :param project_id: id used for lookup
    :param user_id: id of the user perfrming the delete operation
    """
    project = get_project_with_id(project_id)
    if project is None:
        raise RuntimeError('No project associated with this id.')
    else:
        access = Access.query.filter(Access.project_id == project_id). \
            filter(Access.user_id == user_id).first()
        database.session.delete(access)
        database.session.commit()
        cleanup(project_id)


def update_project_with_id(project_id, new_name, new_description):
    """
    Updates project associated with given id
    :param project_id: id used for lookup
    :param new_name: value to update the project's name with
    :param new_description: value to update the project's description with
    """
    project = get_project_with_id(project_id)
    if project is None:
        raise RuntimeError('No project associated with this id.')
    else:
        project.name = new_name
        project.description = new_description
        database.session.commit()


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
