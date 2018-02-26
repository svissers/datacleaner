from flask import Flask
from flask_testing import TestCase
import unittest
import db_manager


# Test cases for db_manager.py ################################################


class DBManagerTests(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] \
            = 'postgresql://flask:flask@localhost:5432/flask_test_db'
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db_manager.db.init_app(app)
        return app

    def setUp(self):
        db_manager.db.create_all(app=self.create_app())

    def tearDown(self):
        db_manager.db.session.remove()
        db_manager.db.drop_all()

    def test_create_user_success(self):
        db_manager.create_user('', '', '', 'test', 'test', 'test')
        self.assertTrue(
            db_manager.Account.query.filter_by(username='test').first())

    def test_create_user_email_already_used(self):
        db_manager.create_user('', '', '', 'used', 'notused1', 'test')
        with self.assertRaises(Exception):
            db_manager.create_user('', '', '', 'used', 'notused2', 'test')

    def test_create_user_username_already_used(self):
        db_manager.create_user('', '', '', 'notused1', 'used', 'test')
        with self.assertRaises(Exception):
            db_manager.create_user('', '', '', 'notused2', 'used', 'test')

    def test_create_user_email_and_username_already_used(self):
        db_manager.create_user('', '', '', 'used', 'used', 'test')
        with self.assertRaises(Exception):
            db_manager.create_user('', '', '', 'used', 'used', 'test')

    def test_validate_login_credentials_success(self):
        db_manager.create_user('', '', '', 'test', 'test', 'test')
        self.assertTrue(db_manager.validate_login_credentials('test', 'test'))

    def test_validate_login_credentials_username_not_found(self):
        self.assertFalse(db_manager.validate_login_credentials('test', 'test'))

    def test_validate_login_credentials_wrong_password(self):
        db_manager.create_user('', '', '', 'test', 'test', 'test')
        self.assertFalse(db_manager.validate_login_credentials('test', 'oops'))


if __name__ == '__main__':
    unittest.main()
