from app import database as db
from sqlalchemy.orm import backref


class Access(db.Model):
    """ Association table for many-to-many relationship User-Project """
    __tablename__ = 'access'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    project_id = db.Column(
        db.Integer,
        db.ForeignKey(
            'project.id',
            ondelete='CASCADE'
        )
    )
    user_id = db.Column(db.Integer, db.ForeignKey('user_data.id'))
    owner = db.Column(db.Boolean, nullable=False)

    user = db.relationship('User', backref=backref('projects',
                                                   cascade="all,delete")
                           )


class Project(db.Model):
    """Represents table holding all projects"""
    __tablename__ = 'project'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(25))
    description = db.Column(db.Text())

    # Dataset is parent of view, thus this relationship helper class
    # datasets = db.relationship('Dataset', backref='project', lazy='dynamic')

    # Project has a many-to-many relationship with User
    # passive_deletes = True to make cascade on delete work correctly
    # otherwise we get SET NULL-like behaviour
    users = db.relationship("Access", backref='project', passive_deletes=True)

    def __init__(self, name, descr):
        self.name = name
        self.description = descr
