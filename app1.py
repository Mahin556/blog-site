from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)

# import pymysql
# pymysql.install_as_MySQLdb()

# configure the SQLite database, relative to the app instance folder
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/db_name'
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:Pass_word1@localhost/devopsclub'
db = SQLAlchemy(app)

class Contacts(db.Model):
    '''
    sno, name phone num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if (request.method == 'POST'):
        '''Add Entry to the Database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        msg = request.form.get('msg')
        entry = Contacts(name=name, email=email, phone_num=phone, msg=msg, date=datetime.now())
        db.session.add(entry)
        db.session.commit()

    return render_template('contact.html')


@app.route("/post")
def post():
    return render_template('post.html')

app.run(debug=True,host='192.168.29.173')


