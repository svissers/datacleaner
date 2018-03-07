from app import database as db
from flask_login import current_user
import pandas as pd
import datetime


class DataAccess(db.Model):
    """
    Represents Dataset access control table
    """

    __tablename__ = 'dataset_access'

    user_id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, user_id, dataset_id):
        self.user_id = user_id
        self.dataset_id = dataset_id


class Dataset(db.Model):
    """
    Represents table holding dataset info
    """

    __tablename__ = 'dataset'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50))
    sql_table_name = db.Column(db.String(50), unique=True)
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
        table_name = table_name.replace(" ", "")
        table_name = table_name.replace("-", "")
        table_name = table_name.replace(":", "")
        table_name = table_name.replace(".", "")
        table_name = "t" + table_name

        print(table_name)

        csv_dataframe.to_sql(name=table_name, con=db_engine, if_exists="fail")

        new_set = Dataset(name, table_name, description)
        db.session.add(new_set)
        db.session.commit()
        user_link = DataAccess(current_user.id, new_set.id)
        db.session.add(user_link)
        db.session.commit()

    @classmethod
    def import_from_zip(cls, file):
        pass

    @classmethod
    def import_from_dump(cls, file):
        pass
