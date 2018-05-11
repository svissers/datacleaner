from app import database as db
import numpy as np
import pandas as pd
import datetime
from app.Data.models import Dataset
from app.Data.operations import get_dataset_with_id
import collections
import string
from wordcloud import WordCloud
try:
    from StringIO import StringIO
except:
    from io import StringIO
from flask import make_response

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


def get_chart_data_numerical(table_name, column):
    df = pd.read_sql_table(table_name, db.engine, columns=[column])
    intervals = pd.cut(df[column], 10, precision=9).apply(str)
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

def get_frequency(table_name, column, stopwords, blacklist = []):
    #filter punctuation
    df = pd.read_sql_table(table_name, db.engine)
    # print df[column]
    # print column
    table = df

    for char in set(string.punctuation):#.difference(['#', '@']):
        table[column] = table[column].str.replace(char, "")

    #lowercase text, for frequency purposes
    table[column] = table[column].str.lower()

    #stop words according to http://xpo6.com/list-of-english-stop-words/
    stopwordlist = ["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also","although","always","am",
                "among","amongst", "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around", "as",  "at", "back","be","became", "because","become","becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down",\
     "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him",\
      "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of",\
       "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that",\
        "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter",\
         "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the"]
    stopwordlist = stopwordlist + ['i', 'am', 'pm']
    #filter stopwords + each row contains list of words in the tweet
    if stopwords:
        blacklist += stopwordlist
    table[column] = table[column].apply(lambda x: list(item.encode('utf-8') for item in x.split() if item not in blacklist))

    words = [item for sublist in table[column] for item in sublist]
    c = collections.Counter(words)

    # rowcount = table.shape[0]
    # threshold = 0.001 * rowcount
    threshold = 0
    # table[column] = table[column].apply(lambda x: [item for item in x if c[item] > threshold])
    #entry --> (word, wordcount)
    frequent_words = [entry for entry in c.most_common() if entry[1] > threshold]
    return frequent_words

def get_wordcloud(table_name, column, stopwords, blacklist = []):
    df = pd.read_sql_table(table_name, db.engine)
    text = "\n".join(df[column])
    wordcloud = WordCloud(width=1000, height=500).generate(text)
    image = wordcloud.to_image()
    # basewidth = 500
    # wpercent = (basewidth / float(image.size[0]))
    # hsize = int((float(image.size[1]) * float(wpercent)))
    # image = image.resize((basewidth, hsize))#, PIL.Image.ANTIALIAS)
    output = StringIO()
    image.save(output, 'PNG', quality=100)
    output.seek(0)
    response=make_response(output.getvalue())
    response.headers['Content-Type'] = 'image/png'

    return response
