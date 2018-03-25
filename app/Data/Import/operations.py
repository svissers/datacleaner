from app.Data.models import Dataset
from app import database
import pandas
import datetime


def upload_csv(name, description, file, project):
    db_engine = database.engine
    csv_dataframe = pandas.read_csv(file)

    table_name = str(datetime.datetime.now())
    table_name = table_name.replace(" ", "")
    table_name = table_name.replace("-", "")
    table_name = table_name.replace(":", "")
    table_name = table_name.replace(".", "")
    original = "og" + table_name
    working_copy = "wc" + table_name

    csv_dataframe.to_sql(name=original, con=db_engine, if_exists="fail")
    csv_dataframe.to_sql(name=working_copy, con=db_engine, if_exists="fail")

    new_dataset = Dataset(name, original, working_copy, description, project)
    database.session.add(new_dataset)
    database.session.commit()
