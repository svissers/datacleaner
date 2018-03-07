from app import database as db
from flask_login import current_user
import pandas as pd
import datetime
from app._user.models import User

class Project(db.Model):
    """Represents a Project"""
    __tablename__ = 'project'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(25))
    description = db.Column(db.Text())

    def __init__(self, name, descr):
        self.name = name
        self.description = descr

    def add_to_database(self):
        """Adds project instance to database"""
        db.session.add(self)
        db.session.commit()

class DataAccess(db.Model):
    """
    Represents Dataset access control table
    """

    __tablename__ = 'dataset_access'

    user_id = db.Column(db.Integer, db.ForeignKey("user_data.id"), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), primary_key=True)

    def __init__(self, user_id, dataset_id):
        self.user_id = user_id
        self.dataset_id = dataset_id


class Dataset(db.Model):
    """
    Represents table holding dataset info
    """

    __tablename__ = 'dataset'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))
    name = db.Column(db.String(50))
    sql_table_name = db.Column(db.String(50))
    description = db.Column(db.String(255))

    def __init__(self, name, table_name, description):
        self.name = name
        self.sql_table_name = table_name
        self.description = description

    @classmethod
    def import_from_csv(cls, name, description, file):
        db_engine = db.engine
        csv_dataframe = pd.read_csv(file)

        table_name = str(datetime.datetime.now())
        table_name.replace(" ", "")
        table_name.replace("-", "")
        table_name.replace(":", "")
        table_name.replace(".", "")

        csv_dataframe.to_sql(name=table_name, con=db_engine, if_exists="fail")

        new_set = Dataset(name, table_name, description)
        db.session.add(new_set)
        user_link = DataAccess(current_user.id, new_set.id)
        db.session.add(user_link)
        db.session.commit()

    @classmethod
    def import_from_zip(cls, file):
        pass

    @classmethod
    def import_from_dump(cls, file):
        pass
