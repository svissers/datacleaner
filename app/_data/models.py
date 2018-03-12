from app import database as db


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

    def add_to_database(self):
        """Adds project access instance to database"""
        db.session.add(self)
        db.session.commit()


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

    def add_to_database(self):
        """Adds dataset instance to database"""
        db.session.add(self)
        db.session.commit()


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
