from app import app, database as db
from app.User import *
from app.Project.operations import *
from app.Data.Import.operations import *
from app.Data.operations import *
from app.Data.helpers import *
from app.Data.Transform.operations import *
from app.Data.View.operations import *
from flask_testing import TestCase
from shutil import copyfile
from os import remove
from sqlalchemy.exc import InvalidRequestError, DataError


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
        for table in db.engine.table_names():
            db.engine.execute('DROP TABLE "{0}"'.format(table))

    def test_upload_csv(self):
        upload_csv('test', 'test', 'CSVs/test.csv', self.project.id)
        self.assertTrue(get_datasets(self.user_id, self.project.id).count() == 1)
        dataset = get_dataset_with_id(1)
        table = table_name_to_object(dataset.working_copy)
        self.assertTrue(db.session.query(table).count() == 10)
        self.assertTrue(db.session.query(table).filter_by(text='test1').first())

    def test_get_dataset(self):
        self.assertTrue(get_datasets(self.user_id, self.project.id).count() == 0)
        upload_csv('test', 'test', 'CSVs/test.csv', self.project.id)
        self.assertTrue(get_datasets(self.user_id, self.project.id).count() == 1)

    def test_get_dataset_with_id(self):
        self.assertIsNone(get_dataset_with_id(1))
        upload_csv('test', 'test', 'CSVs/test.csv', self.project.id)
        self.assertIsNotNone(get_dataset_with_id(1))
        self.assertTrue(get_dataset_with_id(1).name == 'test')

    def test_delete_dataset(self):
        upload_csv('test', 'test', 'CSVs/test.csv', self.project.id)
        self.assertTrue(get_datasets(self.user_id, self.project.id).count() == 1)
        delete_dataset_with_id(1)
        self.assertTrue(get_datasets(self.user_id, self.project.id).count() == 0)

    def test_update_dataset(self):
        upload_csv('test', 'test', 'CSVs/test.csv', self.project.id)
        self.assertTrue(db.session.query(Dataset).filter_by(name='test').first())
        self.assertIsNone(db.session.query(Dataset).filter_by(name='test2').first())
        self.assertTrue(db.session.query(Dataset).filter_by(description='test').first())
        self.assertIsNone(db.session.query(Dataset).filter_by(description='test2').first())
        update_dataset_with_id(1, 'test2', 'test2')
        self.assertTrue(db.session.query(Dataset).filter_by(name='test2').first())
        self.assertIsNone(db.session.query(Dataset).filter_by(name='test').first())
        self.assertTrue(db.session.query(Dataset).filter_by(description='test2').first())
        self.assertIsNone(db.session.query(Dataset).filter_by(description='test').first())

    def test_upload_join(self):
        copyfile('CSVs/left.csv', 'file_queue/left.csv')
        copyfile('CSVs/right.csv', 'file_queue/right.csv')
        upload_joined('cross join', 'test', 'test', 'left.csv', 'KEY1', 'right.csv', 'KEY1', self.project.id)
        dataset = get_dataset_with_id(1)
        table = table_name_to_object(dataset.working_copy)
        self.assertTrue(db.session.query(table).count() == 16)
        self.assertTrue(len(table.columns) == 9)
        upload_joined('left outer join', 'test', 'test', 'left.csv', 'KEY1', 'right.csv', 'KEY1', self.project.id)
        dataset = get_dataset_with_id(2)
        table = table_name_to_object(dataset.working_copy)
        self.assertTrue(db.session.query(table).count() == 5)
        self.assertTrue(len(table.columns) == 8)
        upload_joined('right outer join', 'test', 'test', 'left.csv', 'KEY1', 'right.csv', 'KEY1', self.project.id)
        dataset = get_dataset_with_id(3)
        table = table_name_to_object(dataset.working_copy)
        self.assertTrue(db.session.query(table).count() == 5)
        self.assertTrue(len(table.columns) == 8)
        upload_joined('full outer join', 'test', 'test', 'left.csv', 'KEY1', 'right.csv', 'KEY1', self.project.id)
        table = table_name_to_object(dataset.working_copy)
        self.assertTrue(db.session.query(table).count() == 5)
        self.assertTrue(len(table.columns) == 8)
        upload_joined('inner join', 'test', 'test', 'left.csv', 'KEY1', 'right.csv', 'KEY1', self.project.id)
        table = table_name_to_object(dataset.working_copy)
        self.assertTrue(db.session.query(table).count() == 5)
        self.assertTrue(len(table.columns) == 8)
        remove('file_queue/left.csv')
        remove('file_queue/right.csv')

    def test_rename_column(self):
        upload_csv('test', 'test', 'CSVs/test.csv', self.project.id)
        dataset = get_dataset_with_id(1)
        table = table_name_to_object(dataset.working_copy)
        self.assertTrue(len(table.columns) == 4)
        self.assertTrue(db.session.query(table).filter_by(number=1).first())
        with self.assertRaises(InvalidRequestError):
            db.session.query(table).filter_by(num=1).first()
        db.session.commit()
        rename_attribute(table.name, 'number', 'num')
        table = table_name_to_object(dataset.working_copy)
        self.assertTrue(db.session.query(table).filter_by(num=1).first())
        with self.assertRaises(InvalidRequestError):
            db.session.query(table).filter_by(number=1).first()
        self.assertTrue(len(table.columns) == 4)

    def test_delete_column(self):
        upload_csv('test', 'test', 'CSVs/test.csv', self.project.id)
        dataset = get_dataset_with_id(1)
        table = table_name_to_object(dataset.working_copy)
        self.assertTrue(len(table.columns) == 4)
        self.assertTrue(db.session.query(table).filter_by(number=1).first())
        db.session.commit()
        delete_attribute(table.name, 'number')
        table = table_name_to_object(dataset.working_copy)
        with self.assertRaises(InvalidRequestError):
            db.session.query(table).filter_by(number=1).first()
        self.assertTrue(len(table.columns) == 3)

    def test_restore_original(self):
        upload_csv('test', 'test', 'CSVs/test.csv', self.project.id)
        dataset = get_dataset_with_id(1)
        table = table_name_to_object(dataset.working_copy)
        delete_attribute(table.name, 'number')
        table = table_name_to_object(dataset.working_copy)
        with self.assertRaises(InvalidRequestError):
            db.session.query(table).filter_by(number=1).first()
        self.assertTrue(len(table.columns) == 3)
        restore_original(table.name)
        table = table_name_to_object(dataset.working_copy)
        self.assertTrue(db.session.query(table).filter_by(number=1).first())
        self.assertTrue(len(table.columns) == 4)

    def test_change_types(self):
        upload_csv('test', 'test', 'CSVs/test.csv', self.project.id)
        dataset = get_dataset_with_id(1)
        table = table_name_to_object(dataset.working_copy)
        col = extract_columns_from_db(table)
        self.assertTrue(col[0][0] == 'number')
        self.assertTrue(col[0][1] == 'DOUBLE')
        self.assertTrue(col[2][0] == 'time')
        self.assertTrue(col[2][1] == 'TIMESTAMP')
        change_attribute_type(table.name, col[0][0], 'TEXT')
        change_attribute_type(table.name, col[2][0], 'DATE')
        table = table_name_to_object(dataset.working_copy)
        col = extract_columns_from_db(table)
        self.assertTrue(col[0][0] == 'number')
        self.assertTrue(col[0][1] == 'TEXT')
        self.assertTrue(col[1][0] == 'text')
        self.assertTrue(col[1][1] == 'TEXT')
        with self.assertRaises(DataError):
            change_attribute_type(table.name, col[0][0], 'DATE')
        with self.assertRaises(DataError):
            change_attribute_type(table.name, col[1][0], 'INTEGER')

    def test_delete_rows(self):
        upload_csv('test', 'test', 'CSVs/test.csv', self.project.id)
        dataset = get_dataset_with_id(1)
        table = table_name_to_object(dataset.working_copy)
        self.assertTrue(db.session.query(table).filter_by(text='test1').first())
        self.assertTrue(db.session.query(table).filter_by(number=1).first())
        delete_rows(table.name, '"text"=\'test1\' or "number"=\'1\'')
        self.assertIsNone(db.session.query(table).filter_by(text='test1').first())
        self.assertIsNone(db.session.query(table).filter_by(number=1).first())

    def test_numeric_operations(self):
        upload_csv('test', 'test', 'CSVs/test.csv', self.project.id)
        dataset = get_dataset_with_id(1)
        table = table_name_to_object(dataset.working_copy)
        self.assertTrue(get_most_frequent_value(table.name, 'text') == ('test1', 2))
        self.assertTrue(get_number_of_values(table.name) == 10)
        self.assertTrue(get_number_of_distinct_values(table.name, 'text') == 9)
        self.assertTrue(get_number_of_null_values(table.name, 'number') == 3)
        self.assertTrue(int(float(get_average_value(table.name, 'number'))) == -146692)
        self.assertTrue(get_maximum_value(table.name, 'number') == 4787)
        self.assertTrue(get_minimum_value(table.name, 'number') == -1034534)

    def test_create_action(self):
        upload_csv('test', 'test', 'CSVs/test.csv', self.project.id)
        self.assertIsNone(db.session.query(Action).filter_by(description='test').first())
        self.assertIsNone(db.session.query(Action).filter_by(dataset_id=1).first())
        self.assertIsNone(db.session.query(Action).filter_by(user_id=self.user_id).first())
        create_action('test', 1, self.user_id)
        self.assertTrue(db.session.query(Action).filter_by(description='test').first())
        self.assertTrue(db.session.query(Action).filter_by(dataset_id=1).first())
        self.assertTrue(db.session.query(Action).filter_by(user_id=self.user_id).first())






