from app import app, database as db
from app.User import *
from app.Project.operations import *
from flask_testing import TestCase
import unittest


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
