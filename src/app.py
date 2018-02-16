from flask import make_response, Flask, request, render_template, redirect, url_for, session, escape, jsonify, send_from_directory

from config import config_data
from database_conn import DBConnection

app = Flask('DataCleaner')
app.debug = True
app.secret_key = '38346ab5755640fb0bc4af4fff10b170aba6ac9ba2660137'

app_data = {}
app_data['app_name'] = config_data['app_name']
connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'] ,dbpass=config_data['dbpass'], dbhost=config_data['dbhost'])





@app.route("/")
def main():
    return render_template('index.html', app_data=app_data)


if __name__ == "__main__":
    app.run()
