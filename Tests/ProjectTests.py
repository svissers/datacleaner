from app import app, database as db
from app.User import *
from app.Project.operations import *
from flask_testing import TestCase


class ProjectTests(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        db.create_all(app=app)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_project(self):
        create_user('first', 'last', 'email', 'uname', 'pw')
        user_id = get_user_with_username('uname').id
        create_project('name', 'desc', user_id)
        project = Project.query.filter_by(name='name').first()
        access = Access.query.\
            filter(Access.project_id == project.id).\
            filter(Access.user_id == user_id).first()
        self.assertTrue(project)
        self.assertTrue(access)

    def test_get_project_with_id(self):
        create_user('first', 'last', 'email', 'uname', 'pw')
        user_id = get_user_with_username('uname').id
        create_project('name', 'desc', user_id)
        project = Project.query.filter_by(name='name').first()
        self.assertTrue(project == get_project_with_id(project.id))

    def test_get_all_projects_for_user(self):
        create_user('first', 'last', 'email', 'uname', 'pw')
        user_id = get_user_with_username('uname').id
        create_project('name1', 'desc1', user_id)
        project1 = Project.query.filter_by(name='name1').first()
        create_project('name2', 'desc2', user_id)
        project2 = Project.query.filter_by(name='name2').first()
        create_project('name3', 'desc3', user_id)
        project3 = Project.query.filter_by(name='name3').first()
        self.assertTrue(get_all_projects_for_user(user_id)
                        ==
                        [project1, project2, project3]
                        )

    def test_delete_project_with_id(self):
        create_user('first', 'last', 'email', 'uname', 'pw')
        user_id = get_user_with_username('uname').id
        create_project('name', 'desc', user_id)
        project = Project.query.filter_by(name='name').first()
        delete_project_with_id(project.id, user_id)
        access = Access.query.\
            filter(Access.project_id == project.id).\
            filter(Access.user_id == user_id).first()
        self.assertIsNone(access)

    def test_project_cleanup(self):
        create_user('first', 'last', 'email', 'uname', 'pw')
        user_id = get_user_with_username('uname').id
        create_project('name', 'desc', user_id)
        project = Project.query.filter_by(name='name').first()
        delete_project_with_id(project.id, user_id)
        project = Project.query.filter_by(name='name').first()
        self.assertIsNone(project)

    def test_update_project_with_id(self):
        create_user('first', 'last', 'email', 'uname', 'pw')
        user_id = get_user_with_username('uname').id
        create_project('name', 'desc', user_id)
        project = Project.query.filter_by(name='name').first()
        update_project_with_id(project.id, 'new_name', 'new_desc')
        updated_project = Project.query.filter_by(id=project.id).first()
        self.assertTrue(updated_project.name == 'new_name')
        self.assertTrue(updated_project.description == 'new_desc')

    def test_share_project(self):
        create_user('first1', 'last1', 'email1', 'uname1', 'pw1')
        create_user('first2', 'last2', 'email2', 'uname2', 'pw2')
        create_user('first3', 'last3', 'email3', 'uname3', 'pw3')
        user_id1 = get_user_with_username('uname1').id
        user_id2 = get_user_with_username('uname2').id
        user_id3 = get_user_with_username('uname3').id
        create_project('name', 'desc', user_id1)
        project = Project.query.filter_by(name='name').first()
        share_project(project.id, user_id2)
        share_project(project.id, user_id3)
        access2 = Access.query.\
            filter(Access.project_id == project.id).\
            filter(Access.user_id == user_id2).first()
        access3 = Access.query.\
            filter(Access.project_id == project.id).\
            filter(Access.user_id == user_id3).first()
        self.assertIsNotNone(access2)
        self.assertIsNotNone(access3)
