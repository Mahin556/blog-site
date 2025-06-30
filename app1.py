from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

load_dotenv()  # Loads variables from .env

import json
app = Flask(__name__)

with open("config.json","r") as c:
    params=json.load(c)["params"]

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USERNAME=os.getenv('GMAIL_USER'), #Load from .env file
    MAIL_PASSWORD=os.getenv('GMAIL_PASS'), #Load from .env file
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True
)
mail = Mail(app)

# import pymysql
# pymysql.install_as_MySQLdb()

# configure the SQLite database, relative to the app instance folder
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/db_name'

if params['local_server'] == True:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_db_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_db_uri']

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
    return render_template("index.html", params=params)

@app.route("/about")
def about():
    return render_template('about.html', params=params)

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

        # Ensure recipient is set
        recipient = os.environ.get('GMAIL_USER')
        if not recipient:
            return "Recipient email is not configured", 500

        # Send Email
        mail_msg = Message(
            subject='New message from ' + name,
            sender=email,
            recipients=[recipient],
            body=msg+ '\nPhone: ' + phone
        )
        mail.send(mail_msg)
    return render_template('contact.html', params=params)


@app.route("/post")
def post():
    return render_template('post.html', params=params)

app.run(debug=True,host='192.168.29.173')


