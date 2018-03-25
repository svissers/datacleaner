from app import database as db
# DON'T REMOVE: Import statement is used from relationship definition
from ..View.models import View


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
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'))

    def __init__(self, name, table_name, description, project):
        self.name = name
        self.sql_table_name = table_name
        self.description = description
        self.project_id = project

    def remove_row(self, id):
        self.query.filter_by(id=id).delete()
        db.session.commit()

    @classmethod
    def get_by_id(cls, dataset_id):
        """Returns dataset info associated with given id"""
        return Dataset.query.filter_by(id=dataset_id).first()
