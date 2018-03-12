from app import app
from flask_testing import TestCase
import unittest
from app._user.models import User, db
from app._data.models import Project


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

    def test_create_project_success(self):
        Project('test', 'test').add_to_database()
        self.assertTrue(Project.query.filter_by(name='test').first())


if __name__ == '__main__':
    unittest.main()