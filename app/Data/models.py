from app import database as db


# Association table for many-to-many relationship User-Project
class Access(db.Model):
    """ Docstring """
    __tablename__ = 'access'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user_data.id'))
    owner = db.Column(db.Boolean, nullable=False)

    user = db.relationship('User', backref='projects')


class Project(db.Model):
    """Represents a Project"""
    __tablename__ = 'project'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(25))
    description = db.Column(db.Text())

    # Dataset is parent of view, thus this relationship helper class
    projects = db.relationship('Dataset', backref='project', lazy='dynamic')

    # Project has a many-to-many relationship with User
    users = db.relationship("Access", backref='project')

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

    # Dataset is parent of view, thus this relationship helper class
    views = db.relationship('View', backref='dataset', lazy='dynamic')

    # Dataset is child of project, thus this foreign key
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    def __init__(self, name, table_name, description, project):
        self.name = name
        self.sql_table_name = table_name
        self.description = description
        self.project_id = project

    def add_to_database(self):
        """Adds dataset instance to database"""
        db.session.add(self)
        db.session.commit()

    def remove_from_database(self):
        db.session.delete(self)
        db.session.commit()

    def remove_row(self, id):
        self.query.filter_by(id=id).delete()
        db.session.commit()

    @classmethod
    def get_by_id(cls, dataset_id):
        """Returns dataset info associated with given id"""
        return Dataset.query.filter_by(id=dataset_id).first()


class View(db.Model):
    """
    Represents table holding view info
    """

    __tablename__ = 'view'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50))
    sql_table_name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(255))

    # View is parent of action, thus this relationship helper class
    actions = db.relationship('Action', backref='view', lazy='dynamic')

    # View is child of dataset, thus this foreign key
    original_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))

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

    # Action is child of view, thus this foreign key
    view_id = db.Column(db.Integer, db.ForeignKey('view.id'))

    # Action is child of user, thus this foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user_data.id'))
