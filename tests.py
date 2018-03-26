from app import app
from flask_testing import TestCase
import unittest
from app._user.models import User, db
from app._data.models import Project, ProjectAccess
from app._data.helpers import create_project, get_projects, share_project_with


# Test cases for _user ################################################

class UserTests(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        db.create_all(app=app)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_user_success(self):
        User('', '', '', 'test', 'test', 'test').add_to_database()
        self.assertTrue(User.query.filter_by(username='test').first())

    def test_create_user_email_already_used(self):
        User('', '', '', 'used', 'notused1', 'test').add_to_database()
        with self.assertRaises(Exception):
            User('', '', '', 'used', 'notused2', 'test').add_to_database()

    def test_create_user_username_already_used(self):
        User('', '', '', 'notused1', 'used', 'test').add_to_database()
        with self.assertRaises(Exception):
            User('', '', '', 'notused2', 'used', 'test').add_to_database()

    def test_create_user_email_and_username_already_used(self):
        User('', '', '', 'used', 'used', 'test').add_to_database()
        with self.assertRaises(Exception):
            User('', '', '', 'used', 'used', 'test').add_to_database()

    def test_validate_login_credentials_success(self):
        User('', '', '', 'test', 'test', 'test').add_to_database()
        self.assertTrue(User.validate_login_credentials('test', 'test')[0])

    def test_validate_login_credentials_username_not_found(self):
        self.assertFalse(User.validate_login_credentials('test', 'test')[0])

    def test_validate_login_credentials_wrong_password(self):
        User('', '', '', 'test', 'test', 'test').add_to_database()
        self.assertFalse(User.validate_login_credentials('test', 'oops')[0])

    def test_get_user(self):
        User('', '', '', 'test', 'test', 'test').add_to_database()
        self.assertTrue(User.get_by_name('test'))
        self.assertFalse(User.get_by_name('test2'))
        self.assertTrue(User.get_by_name('test').email == 'test')

    def test_get_user_by_id(self):
        User('', '', '', 'test', 'test', 'test').add_to_database()
        userid = User.get_by_name('test').id
        self.assertTrue(User.get_by_id(userid))
        self.assertFalse(User.get_by_id(userid + 1))

    def test_edit_user_success(self):
        User('test', 'test', '', 'test', 'test', 'test').add_to_database()
        userid = User.get_by_name('test').id
        User.update_by_id(userid, 'test2', 'test2', 'test2', 'test2', 'test2', 'test2')
        self.assertTrue(User.get_by_name('test2'))
        self.assertFalse(User.get_by_name('test'))
        User.update_by_id(userid, '', '', '', 'test3', '', '')
        self.assertTrue(User.get_by_name('test2').email == 'test3')

    def test_edit_user_no_changes(self):
        User('test', 'test', 'test', 'test', 'test', 'test').add_to_database()
        userid = User.get_by_name('test').id
        User.update_by_id(userid, '', '', '', '', '', '')
        self.assertTrue(User.get_by_id(userid).username == 'test')
        self.assertTrue(User.get_by_id(userid).email == 'test')
        self.assertTrue(User.get_by_id(userid).first_name == 'test')
        self.assertTrue(User.get_by_id(userid).last_name == 'test')
        self.assertTrue(User.get_by_id(userid).organization == 'test')

    def test_edit_user_username_already_used(self):
        User('', '', '', 'test', 'test', 'test').add_to_database()
        User('', '', '', 'test2', 'test2', 'test2').add_to_database()
        with self.assertRaises(Exception):
            userid = User.get_by_name('test').id
            User.update_by_id(userid, '', '', '', '', 'test2', '')

    def test_edit_user_email_already_used(self):
        User('', '', '', 'test', 'test', 'test').add_to_database()
        User('', '', '', 'test2', 'test2', 'test2').add_to_database()
        with self.assertRaises(Exception):
            userid = User.get_by_name('test').id
            User.update_by_id(userid, '', '', '', 'test2', '', '')

    def test_edit_admin_username(self):
        User('', '', '', 'admin', 'admin', 'admin').add_to_database()
        userid = User.get_by_name('admin').id
        self.assertIsNone(User.update_by_id(userid, '', '', '', '', 'admin', ''))
        with self.assertRaises(Exception):
            User.update_by_id(userid, '', '', '', '', 'test', '')

    def test_init_admin(self):
        self.assertFalse(User.get_by_name('admin'))
        User.init_admin()
        self.assertTrue(User.get_by_name('admin'))


# Test cases for _data ################################################

class DataTests(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        db.create_all(app=app)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_project(self):
        Project('test', 'test').add_to_database()
        self.assertTrue(Project.query.filter_by(name='test').first())

    def test_project_access(self):
        User('', '', '', 'test', 'test', 'test').add_to_database()
        userid = User.get_by_name('test').id
        project = Project('test', 'test')
        project.add_to_database()
        projectid = project.id
        ProjectAccess(userid, projectid, userid).add_to_database()
        self.assertTrue(ProjectAccess.query.filter_by(project_id=projectid).first())
        self.assertTrue(ProjectAccess.query.filter_by(user_id=userid).first())

    def test_create_project(self):
        User('', '', '', 'test', 'test', 'test').add_to_database()
        userid = User.get_by_name('test').id
        create_project('test', 'test', userid)
        self.assertTrue(Project.query.filter_by(name='test').first())
        self.assertTrue(Project.query.filter_by(description='test').first())
        self.assertTrue(ProjectAccess.query.filter_by(user_id=userid).first())

    def test_get_projects(self):
        User('', '', '', 'test', 'test', 'test').add_to_database()
        userid = User.get_by_name('test').id
        create_project('test', 'test', userid)
        create_project('test2', 'test2', userid)
        projects = get_projects(userid, True)
        self.assertTrue(len(projects) == 2)
        for project in projects:
            db_project = Project.query.filter_by(id=project[0]).first()
            self.assertTrue(db_project.name == project[1])
            self.assertTrue(db_project.description == project[2])

    def test_share(self):
        User('', '', '', 'test', 'test', 'test').add_to_database()
        User('', '', '', 'test2', 'test2', 'test2').add_to_database()
        userid = User.get_by_name('test').id
        userid2 = User.get_by_name('test2').id
        create_project('test', 'test', userid)
        project_id = Project.query.filter_by(name='test').first().id
        projects = get_projects(userid2, True)
        self.assertTrue(len(projects) == 0)
        share_project_with(project_id, userid2)
        projects = get_projects(userid2, True)
        self.assertTrue(len(projects) == 1)


class FrontEnd(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        pass

    def test_home(self):
        result = self.app.get('/user/signup')
        self.assertEqual(result.status_code, 200)


if __name__ == '__main__':
    unittest.main()
