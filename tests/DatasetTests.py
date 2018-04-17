from app import app, database as db
from app.User import *
from app.Project.operations import *
from app.Data.Import.operations import *
from app.Data.operations import *
from app.Data.helpers import *
from flask_testing import TestCase


class DatasetTests(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        db.create_all(app=app)
        create_user('first', 'last', 'email', 'uname', 'pw')
        self.user_id = get_user_with_username('uname').id
        create_project('name', 'desc', self.user_id)
        self.project = Project.query.filter_by(name='name').first()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_upload_csv(self):
        upload_csv('test', 'test', 'CSVs/test.csv', self.project.id)
        self.assertTrue(get_datasets(self.user_id, self.project.id).count() == 1)
        dataset = get_dataset_with_id(1)
        table = table_name_to_object(dataset.working_copy)
        self.assertTrue(db.session.query(table).count() == 10)
        self.assertTrue(db.session.query(table).filter_by(test='test1').first())


