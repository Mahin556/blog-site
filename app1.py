from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import math

load_dotenv()  # Loads variables from .env

import json
app = Flask(__name__)

app.secret_key = 'super_secret_key'

with open("config.json","r") as c:
    params=json.load(c)["params"]

app.config['UPLOAD_FOLDER']=params['upload_location']

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

class Posts(db.Model):
    '''
    sno, slug, title, content, date, img_name, tagline
    '''
    sno = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(25), nullable=False)
    title = db.Column(db.String(30), nullable=False)
    content = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_name = db.Column(db.String(30), nullable=True)
    tagline = db.Column(db.String(20), nullable=False)


@app.route("/")
def home():
    posts=Posts.query.filter_by().all()
    last=math.ceil(len(posts)/int(params['no_of_posts']))  # give greatest integer
    page = request.args.get('page')
    if not str(page).isnumeric():  #checks if the value is purely numeric (like '1', '2', etc.).
        page = 1                   #If it's not numeric (e.g., None, 'abc', empty string), it defaults to page = 1.
    page = int(page)               #ensures page is now an integer (for math, slicing, etc).
    posts = posts[(page - 1) * int(params['no_of_posts']) : page * int(params['no_of_posts'])]   #Slice the Posts List for This Page
    if page == 1:
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif page == last:
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)
    
    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)


@app.route("/uploader", methods=['GET','POST'])
def uploader():
    if ( 'user' in session) and ( session['user'] == params['admin_user'] ):
        if request.method == 'POST':
            f = request.files['filename']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded Successfully"
        
@app.route("/logout")
def logout():
    session.pop('user')
    return redirect("/dashboard")

@app.route("/delete/<string:post_sno>", methods=['GET', 'POST'])
def delete(post_sno):
    if ( 'user' in session) and ( session['user'] == params['admin_user'] ):
        post = Posts.query.filter_by(sno=post_sno).first() #without first() return list
        if post:
            db.session.delete(post)
            db.session.commit()
        else:
            return "Post not found", 404
    return redirect("/dashboard")

@app.route("/edit/<string:post_sno>", methods=['GET', 'POST'])
def edit(post_sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            content = request.form.get('content')
            slug = request.form.get('slug')
            img_name = request.form.get('img_name')
            date = datetime.now()

            if post_sno == '0':
                # Creating a new post
                post = Posts(slug=slug, title=title, content=content,
                             tagline=tagline, img_name=img_name, date=date)
                db.session.add(post)
                db.session.commit()
            else:
                # Editing existing post — make sure to convert post_sno to int
                post = Posts.query.filter_by(sno=int(post_sno)).first()
                if post:
                    post.title = title
                    post.tagline = tagline
                    post.content = content
                    post.slug = slug
                    post.img_name = img_name
                    post.date = date
                    db.session.commit()
                else:
                    return "Post not found", 404

            return redirect('/post/' + post.slug)

        # GET method — prefill form
        post = Posts.query.filter_by(sno=int(post_sno)).first() if post_sno != '0' else None
        return render_template("edit.html", params=params, post=post, sno=post_sno)

    return render_template("login.html", params=params)

@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/dashboard", methods = ['GET', 'POST'])
def dashboard():
    # validating if user already login
    if ( 'user' in session) and ( session['user'] == params['admin_user'] ):
        posts=Posts.query.filter_by().all()
        return render_template('dashboard.html', params=params, posts=posts)
    
    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        # Redirect to Admin dashboard
        if ( username == params['admin_user'] and userpass == params['admin_password']):
            # set the session variable
            session['user'] = username
            posts=Posts.query.filter_by().all()
            return render_template('dashboard.html', params=params, posts=posts)
    
    return render_template('login.html', params=params)

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


@app.route("/post/<string:post_slug>", methods = ['GET'])
def post_get(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)


app.run(debug=True,host='0.0.0.0')


