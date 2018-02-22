from flask import make_response, Flask, request, render_template, redirect, url_for, session, escape, jsonify, send_from_directory
from pbkdf2 import crypt
from config import config_data
from database_conn import DBConnection

app = Flask('DataCleaner')
app.debug = True
app.secret_key = '38346ab5755640fb0bc4af4fff10b170aba6ac9ba2660137'

app_data = {}
app_data['app_name'] = config_data['app_name']
connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'] ,dbpass=config_data['dbpass'], dbhost=config_data['dbhost'])


@app.route("/")
def main(errors=None):
    return render_template('index.html', app_data=app_data, errors=errors)


@app.route("/login/", methods=["POST", "GET"])
def login():
    cursor = connection.get_cursor()
    user = str(request.form.get("username"))
    pw = str(request.form.get("password"))
    cursor.execute("select username, password, name, email, active, admin from Users where username=%s;", [user])
    result = cursor.fetchall()
    print result
    if len(result) == 0:
        return main(errors=["No user found"])

    pwhash = result[0][1]
    if pwhash == crypt(pw, pwhash):
        #login successful
        # session["type"] = result[0][1]
        # session["userid"] = result[0][2]
        return redirect(url_for("home"))
    else:
        return main(errors=["Wrong password"])

@app.route("/register/", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        cursor = connection.get_cursor()
        #dit, maar dan met de juiste info, zie init.sql wat een user allemaal moet hebben
        username = str(request.form.get("username"))
        password = str(request.form.get("password"))
        name = ""
        email = ""
        admin = True

        #TODO check if username already exists

        cursor.execute("insert into users (username, password, name, email, active,  admin) values (%s, %s, %s, %s, %s, %s)", [username,crypt(password), name, email, True, admin])
        #na een update moet je altijd connection.commit() oproepen
        connection.commit()
        return render_template('hw.html', app_data=app_data)

    elif request.method == "GET":
        return render_template('register.html', app_data=app_data)

@app.route("/home/", methods=["POST", "GET"])
def home():
    cursor = connection.get_cursor()
    cursor.execute("select username, password, name, email, active, admin from Users;", [])
    result = cursor.fetchall()
    for row in result:
        print row
    return render_template('hw.html', app_data=app_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
