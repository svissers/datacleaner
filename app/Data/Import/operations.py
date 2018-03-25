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
    table_name = "t" + table_name

    csv_dataframe.to_sql(name=table_name, con=db_engine, if_exists="fail")

    new_dataset = Dataset(name, table_name, description, project)
    database.session.add(new_dataset)
    database.session.commit()
