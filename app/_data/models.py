from app import database as db
from flask_login import current_user
import pandas as pd
import datetime
from app._user.models import User


class ProjectAccess(db.Model):
    """
    Represents Project access control table
    """

    __tablename__ = 'project_access'

    user = db.relationship('User', backref='user_data')
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user_data.id"),
        primary_key=True
    )
    project = db.relationship('Project', backref='project')
    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project.id"),
        primary_key=True
    )

    def __init__(self, user_id, project_id):
        self.user_id = user_id
        self.project_id = project_id


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


class Dataset(db.Model):
    """
    Represents table holding dataset info
    """

    __tablename__ = 'dataset'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50))
    sql_table_name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(255))

    project = db.relationship('Project', backref='project1')
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))

    def __init__(self, name, table_name, description, project):
        self.name = name
        self.sql_table_name = table_name
        self.description = description
        self.project_id = project

    @classmethod
    def import_from_csv(cls, name, description, file, project):
        db_engine = db.engine
        csv_dataframe = pd.read_csv(file)

        table_name = str(datetime.datetime.now())
        table_name = table_name.replace(" ", "")
        table_name = table_name.replace("-", "")
        table_name = table_name.replace(":", "")
        table_name = table_name.replace(".", "")
        table_name = "t" + table_name

        print(table_name)

        csv_dataframe.to_sql(name=table_name, con=db_engine, if_exists="fail")

        new_set = Dataset(name, table_name, description, project)
        db.session.add(new_set)
        db.session.commit()
        user_link = ProjectAccess(current_user.id, project)
        db.session.add(user_link)
        db.session.commit()

    @classmethod
    def import_from_zip(cls, file):
        pass

    @classmethod
    def import_from_dump(cls, file):
        pass


class View(db.Model):
    """
    Represents table holding view info
    """

    __tablename__ = 'view'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50))
    sql_table_name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(255))

    original = db.relationship('Dataset', backref='dataset')
    original_id = db.Column(db.Integer, db.ForeignKey("dataset.id"))

    def __init__(self, name, table_name, description):
        self.name = name
        self.sql_table_name = table_name
        self.description = description


class Action(db.Model):
    """ Vieze docstring """

    __tablename__ = 'action'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    time = db.Column(db.DateTime)
    description = db.Column(db.String(255))

    view = db.relationship('View', backref='view')
    view_id = db.Column(db.Integer, db.ForeignKey("view.id"))

    user = db.relationship('User', backref='user_data1')
    user_id = db.Column(db.Integer, db.ForeignKey("user_data.id"))
