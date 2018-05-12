from app import database as db
import numpy as np
import pandas as pd
import datetime
from app.Data.models import Dataset
from app.Data.operations import get_dataset_with_id


def get_most_frequent_value(table_name, column):
    return db.engine.execute(
        'SELECT "{0}", COUNT("{0}") AS "frequency" '
        'FROM "{1}" '
        'GROUP BY "{0}" '
        'ORDER BY "frequency" DESC '
        'LIMIT 1;'
        .format(column, table_name)
    ).first()


def get_number_of_values(table_name):
        return db.engine.execute(
            'SELECT COUNT(*) '
            'FROM "{0}" '
            .format(table_name)
        ).first()[0]


def get_number_of_distinct_values(table_name, column):
    return db.engine.execute(
        'SELECT COUNT(DISTINCT("{0}")) '
        'FROM "{1}" '
        .format(column, table_name)
    ).first()[0]


def get_number_of_null_values(table_name, column, text_type=False):
    if text_type:
        return db.engine.execute(
            'SELECT COUNT(*) '
            'FROM "{1}" '
            'WHERE "{0}" IS NULL OR "{0}" = \'\''
            .format(column, table_name)
        ).first()[0]
    else:
        return db.engine.execute(
            'SELECT COUNT(*) '
            'FROM "{1}" '
            'WHERE "{0}" IS NULL'
            .format(column, table_name)
        ).first()[0]


def get_average_value(table_name, column):
    return str(
        db.engine.execute(
            'SELECT AVG("{0}") '
            'FROM "{1}" '
            .format(column, table_name)
        ).first().avg
    )


def get_maximum_value(table_name, column):
    return db.engine.execute(
        'SELECT "{0}" '
        'FROM "{1}" '
        'WHERE "{0}" IS NOT NULL '
        'ORDER BY "{0}" DESC '
        'LIMIT 1;'
        .format(column, table_name)
    ).first()[0]


def get_minimum_value(table_name, column):
    return db.engine.execute(
        'SELECT "{0}" '
        'FROM "{1}" '
        'WHERE "{0}" IS NOT NULL '
        'ORDER BY "{0}" ASC '
        'LIMIT 1;'
        .format(column, table_name)
    ).first()[0]


def get_chart_data_numerical(table_name, column, bins=10, eq='width'):
    df = pd.read_sql_table(table_name, db.engine, columns=[column])
    edges = []
    if eq == 'width':
        min_val = df.min()
        max_val = df.max()
        width = (max_val + min_val)/bins
        edges = np.arange(min_val, max_val, width)
    elif eq == 'freq':
        attr_length = len(df)
        elements_per_interval = attr_length // bins
        sorted_data = list(df[column].sort_values())
        selector = 0
        while selector < attr_length:
            try:
                edges.append(sorted_data[selector])
                selector += elements_per_interval
            except IndexError:
                pass
        if edges[-1] != sorted_data[-1] and len(edges) == bins + 1:
            edges[-1] = sorted_data[-1]
        elif edges[-1] != sorted_data[-1] and len(edges) != bins + 1:
            edges.append(sorted_data[-1])

        # Extend outer edges with 0.1% to include min and max values
        edges[0] = edges[0] - edges[0] * 0.001
        edges[-1] = edges[-1] + edges[-1] * 0.001

    intervals = pd.cut(df[column], edges).apply(str)
    data = {}
    for row in intervals:
        if row in data:
            data[row] += 1
        else:
            data[row] = 1
    result = []
    for key in data:
        if isinstance(key, str) and key is not None:
            result.append((key, data[key]))
    result.sort(key=lambda tup: tup[0])
    labels, values = map(list, zip(*result))
    colours = []
    body_colours = []
    border_colours = []
    while len(colours) < len(labels):
        random_colour = list(np.random.choice(range(256), size=3))
        if random_colour not in colours:
            colours.append(random_colour)
            body_colours.append('rgba' + str(tuple(random_colour + [0.2])))
            border_colours.append('rgba' + str(tuple(random_colour + [1.0])))
    return labels, values, body_colours, border_colours


def get_chart_data_categorical(table_name, column):
    df = pd.read_sql_table(table_name, db.engine, columns=[column])
    data = {}
    for value in df[column]:
        if value in data:
            data[value] += 1
        else:
            data[value] = 1
    result = []
    for key in data:
        if key is not None:
            result.append((key, data[key]))
    result.sort(key=lambda tup: tup[0])
    labels, values = map(list, zip(*result))
    colours = []
    body_colours = []
    border_colours = []
    while len(colours) < len(labels):
        random_colour = list(np.random.choice(range(256), size=3))
        if random_colour not in colours:
            colours.append(random_colour)
            body_colours.append('rgba' + str(tuple(random_colour + [0.2])))
            border_colours.append('rgba' + str(tuple(random_colour + [1.0])))
    return labels, values, body_colours, border_colours


def get_chart_data_date_or_timestamp(table_name, column, bins):
    df = pd.read_sql_table(table_name, db.engine, columns=[column])
    data = {}
    if bins == 'YEAR':
        df = df[column].dt.year
    elif bins == 'MONTH':
        df = df[column].dt.month
        data = {key: 0 for key in range(1, 13)}
    elif bins == 'WOY':
        df = df[column].dt.week
        data = {key: 0 for key in range(1, 53)}
    elif bins == 'QUARTER':
        df = df[column].dt.quarter
        data = {key: 0 for key in range(1, 5)}
    elif bins == 'DOW':
        df = df[column].dt.weekday
        data = {key: 0 for key in range(7)}
    elif bins == 'TOD':
        df = df[column].dt.hour
        data = {key: 0 for key in range(24)}
    for value in df:
        if value in data:
            data[value] += 1
        elif value not in data and bins == 'YEAR':
            data[value] = 1
    result = []

    for key in data:
        if key is not None:
            result.append((key, data[key]))
    result.sort(key=lambda tup: tup[0])
    labels, values = map(list, zip(*result))
    if bins == 'MONTH':
        labels = ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November',
                  'December'
                  ]
    elif bins == 'DOW':
        labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                  'Saturday', 'Sunday'
                  ]
    elif bins == 'QUARTER':
        labels = ['Q1', 'Q2', 'Q3', 'Q4']
    colours = []
    body_colours = []
    border_colours = []
    while len(colours) < len(labels):
        random_colour = list(np.random.choice(range(256), size=3))
        if random_colour not in colours:
            colours.append(random_colour)
            body_colours.append('rgba' + str(tuple(random_colour + [0.2])))
            border_colours.append('rgba' + str(tuple(random_colour + [1.0])))
    return labels, values, body_colours, border_colours


def export_csv(table_name, delim=',', quote='"', null=''):
    try:
        df = pd.read_sql_table(table_name, db.engine)
        df = df.drop('index', 1)
        return df.to_csv(sep=delim, quotechar=quote, na_rep=null, index=False)
    except:
        print('AN ERROR OCCURED WHILE EXPORTING TO CSV')


def join_datasets(left_id,
                  left_column,
                  right_id,
                  right_column,
                  join_type,
                  name,
                  desc):
    db_engine = db.engine

    dataset_left = get_dataset_with_id(left_id)
    dataset_right = get_dataset_with_id(right_id)

    dataframe_left = pd.read_sql_table(
        table_name=dataset_left.working_copy,
        con=db_engine,
        index_col='index'
    )
    dataframe_right = pd.read_sql_table(
        table_name=dataset_right.working_copy,
        con=db_engine,
        index_col='index'
    )
    result_dataframe = None

    print(dataframe_left)
    print(dataframe_right)

    suffixes = ('left', 'right')

    if join_type == "cross":
        dataframe_left['temp'] = 0
        dataframe_right['temp'] = 0
        result_dataframe = pd.merge(dataframe_left, dataframe_right, on='temp')
        result_dataframe = result_dataframe.drop(labels=['temp'], axis=1)
    elif join_type == "inner join":
        result_dataframe = pd.merge(
            dataframe_left,
            dataframe_right,
            left_on=left_column,
            right_on=right_column,
            how='inner',
            suffixes=suffixes
        )
    elif join_type == "left outer":
        result_dataframe = pd.merge(
            dataframe_left,
            dataframe_right,
            left_on=left_column,
            right_on=right_column,
            how='left',
            suffixes=suffixes
        )
    elif join_type == "right outer":
        result_dataframe = pd.merge(
            dataframe_left,
            dataframe_right,
            left_on=left_column,
            right_on=right_column,
            how='right',
            suffixes=suffixes
        )
    elif join_type == "full outer":
        result_dataframe = pd.merge(
            dataframe_left,
            dataframe_right,
            left_on=left_column,
            right_on=right_column,
            how='outer',
            suffixes=suffixes
        )

    table_name = str(datetime.datetime.now())
    table_name = table_name.replace(" ", "")
    table_name = table_name.replace("-", "")
    table_name = table_name.replace(":", "")
    table_name = table_name.replace(".", "")
    original = "og" + table_name
    working_copy = "wc" + table_name

    result_dataframe.to_sql(name=original, con=db_engine, if_exists="fail")
    result_dataframe.to_sql(name=working_copy, con=db_engine, if_exists="fail")

    new_dataset = Dataset(
        name,
        original,
        working_copy,
        desc,
        dataset_left.project.id
    )
    db.session.add(new_dataset)
    db.session.commit()
