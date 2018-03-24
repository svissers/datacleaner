from app import app, database as db
from app.User import *
from flask_testing import TestCase
import unittest
# from app.Data.models import Project, ProjectAccess
# from app.Data.helpers import create_project, get_projects, share_project_with


# Test cases for User ################################################

class UserTests(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        db.create_all(app=app)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_user_success(self):
        create_user('', '', 'test', 'test', 'test')
        self.assertTrue(get_user_with_username('test'))

    def test_create_user_email_already_used(self):
        create_user('', '', 'used', 'notused1', 'test')
        with self.assertRaises(RuntimeError):
            create_user('', '', 'used', 'notused2', 'test')

    def test_create_user_username_already_used(self):
        create_user('', '', 'notused1', 'used', 'test')
        with self.assertRaises(RuntimeError):
            create_user('', '', 'notused2', 'used', 'test')

    def test_create_user_email_and_username_already_used(self):
        create_user('', '', 'used', 'used', 'test')
        with self.assertRaises(RuntimeError):
            create_user('', '', 'used', 'used', 'test')

    def test_validate_login_credentials_success(self):
        create_user('', '', 'test', 'test', 'test')
        self.assertTrue(validate_login_credentials('test', 'test')[0])

    def test_validate_login_credentials_username_not_found(self):
        self.assertFalse(validate_login_credentials('test', 'test')[0])

    def test_validate_login_credentials_wrong_password(self):
        create_user('', '', 'test', 'test', 'test')
        self.assertFalse(validate_login_credentials('test', 'oops')[0])

    def test_get_user(self):
        create_user('', '', 'test', 'test', 'test')
        self.assertTrue(get_user_with_username('test'))
        self.assertFalse(get_user_with_username('test2'))
        self.assertTrue(get_user_with_username('test').email == 'test')

    def test_get_user_by_id(self):
        create_user('', '', 'test', 'test', 'test')
        userid = get_user_with_username('test').id
        self.assertTrue(get_user_with_id(userid))
        self.assertFalse(get_user_with_id(userid + 1))

    def test_edit_user_success(self):
        create_user('test', '', 'test', 'test', 'test')
        userid = get_user_with_username('test').id
        update_user_with_id(userid, 'test2', 'test2', 'test2', 'test2', 'test2')
        self.assertTrue(get_user_with_username('test2'))
        self.assertFalse(get_user_with_username('test'))
        update_user_with_id(userid, '', '', 'test3', '', '')
        self.assertTrue(get_user_with_username('test2').email == 'test3')

    def test_edit_user_no_changes(self):
        create_user('test', 'test', 'test', 'test', 'test')
        userid = get_user_with_username('test').id
        update_user_with_id(userid, '', '', '', '', '')
        self.assertTrue(get_user_with_id(userid).username == 'test')
        self.assertTrue(get_user_with_id(userid).email == 'test')
        self.assertTrue(get_user_with_id(userid).first_name == 'test')
        self.assertTrue(get_user_with_id(userid).last_name == 'test')

    def test_edit_user_username_already_used(self):
        create_user('', '', 'test', 'test', 'test')
        create_user('', '', 'test2', 'test2', 'test2')
        with self.assertRaises(RuntimeError):
            userid = get_user_with_username('test').id
            update_user_with_id(userid, '', '', '', 'test2', '')

    def test_edit_user_email_already_used(self):
        create_user('', '', 'test', 'test', 'test')
        create_user('', '', 'test2', 'test2', 'test2')
        with self.assertRaises(RuntimeError):
            userid = get_user_with_username('test').id
            update_user_with_id(userid, '', '', 'test2', '', '')

    def test_edit_admin_username(self):
        create_user('', '', 'admin', 'admin', 'admin')
        userid = get_user_with_username('admin').id
        self.assertIsNone(update_user_with_id(userid, '', '', '', 'admin', ''))
        with self.assertRaises(RuntimeError):
            update_user_with_id(userid, '', '', '', 'test', '')

    def test_init_admin(self):
        self.assertFalse(get_user_with_username('admin'))
        init_admin()
        self.assertTrue(get_user_with_username('admin'))


# Test cases for Data ################################################

# class DataTests(TestCase):
#     def create_app(self):
#         return app
#
#     def setUp(self):
#         db.create_all(app=app)
#
#     def tearDown(self):
#         db.session.remove()
#         db.drop_all()
#
#     def test_project(self):
#         Project('test', 'test').add_to_database()
#         self.assertTrue(Project.query.filter_by(name='test').first())
#
#     def test_project_access(self):
#         User('', '', '', 'test', 'test', 'test').add_to_database()
#         userid = get_by_name('test').id
#         project = Project('test', 'test')
#         project.add_to_database()
#         projectid = project.id
#         ProjectAccess(userid, projectid, userid).add_to_database()
#         self.assertTrue(ProjectAccess.query.filter_by(project_id=projectid).first())
#         self.assertTrue(ProjectAccess.query.filter_by(user_id=userid).first())
#
#     def test_create_project(self):
#         User('', '', '', 'test', 'test', 'test').add_to_database()
#         userid = get_by_name('test').id
#         create_project('test', 'test', userid)
#         self.assertTrue(Project.query.filter_by(name='test').first())
#         self.assertTrue(Project.query.filter_by(description='test').first())
#         self.assertTrue(ProjectAccess.query.filter_by(user_id=userid).first())
#
#     def test_get_projects(self):
#         User('', '', '', 'test', 'test', 'test').add_to_database()
#         userid = get_by_name('test').id
#         create_project('test', 'test', userid)
#         create_project('test2', 'test2', userid)
#         projects = get_projects(userid, True)
#         self.assertTrue(len(projects) == 2)
#         for project in projects:
#             db_project = Project.query.filter_by(id=project[0]).first()
#             self.assertTrue(db_project.name == project[1])
#             self.assertTrue(db_project.description == project[2])
#
#     def test_share(self):
#         User('', '', '', 'test', 'test', 'test').add_to_database()
#         User('', '', '', 'test2', 'test2', 'test2').add_to_database()
#         userid = get_by_name('test').id
#         userid2 = get_by_name('test2').id
#         create_project('test', 'test', userid)
#         project_id = Project.query.filter_by(name='test').first().id
#         projects = get_projects(userid2, True)
#         self.assertTrue(len(projects) == 0)
#         share_project_with(project_id, userid2)
#         projects = get_projects(userid2, True)
#         self.assertTrue(len(projects) == 1)


if __name__ == '__main__':
    unittest.main()
