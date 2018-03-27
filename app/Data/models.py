from app import database as db
from datetime import datetime


class Dataset(db.Model):
    """
    Represents table holding dataset info
    """

    __tablename__ = 'dataset'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50))
    original_data = db.Column(db.String(50), unique=True)
    working_copy = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(255))

    # View is parent of action, thus this relationship helper class
    actions = db.relationship(
        'Action',
        backref='dataset',
        lazy='dynamic',
        passive_deletes=True
    )

    # Dataset is child of project, thus this foreign key
    project_id = db.Column(
        db.Integer,
        db.ForeignKey(
            'project.id',
            ondelete='CASCADE'
        )
    )

    def __init__(self, name, original, working, description, project):
        self.name = name
        self.original_data = original
        self.working_copy = working
        self.description = description
        self.project_id = project


class Action(db.Model):
    """ Vieze docstring """

    __tablename__ = 'action'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255))

    # Action is child of view, thus this foreign key
    dataset_id = db.Column(
        db.Integer,
        db.ForeignKey(
            'dataset.id',
            ondelete='CASCADE'
        )
    )

    # Action is child of user, thus this foreign key
    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            'user_data.id',
            ondelete='SET NULL')
    )

    def __init__(self, description, dataset_id, user_id):
        self.description = description
        self.dataset_id = dataset_id
        self.user_id = user_id
