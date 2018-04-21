from app import database as db
from sqlalchemy.orm import backref
# DON'T REMOVE: Import statement is used from relationship definition


class Access(db.Model):
    """ Association table for many-to-many relationship User-Project """
    __tablename__ = 'access'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    project_id = db.Column(
        db.Integer,
        db.ForeignKey('project.id',ondelete='CASCADE'),
        nullable=False
    )
    user_id = db.Column(db.Integer,
                        db.ForeignKey('user_data.id'),
                        nullable=False
                        )

    user = db.relationship('User',
                           backref=backref('projects', cascade="all,delete")
                           )


class Project(db.Model):
    """Represents table holding all projects"""
    __tablename__ = 'project'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    owner_id = db.Column(db.Integer,
                         db.ForeignKey('user_data.id'),
                         nullable=False)

    # Dataset is parent of view, thus this relationship helper class
    datasets = db.relationship('Dataset',
                               backref=backref('project'),
                               lazy='dynamic', passive_deletes=True
                               )

    # Project has a many-to-many relationship with User
    # passive_deletes = True to make cascade on delete work correctly
    # otherwise we get SET NULL-like behaviour
    users = db.relationship("Access", backref='project', passive_deletes=True)

    def __init__(self, name, descr, creator):
        self.name = name
        self.description = descr
        self.owner_id = creator
