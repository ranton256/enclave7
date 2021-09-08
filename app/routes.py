from flask import render_template, request, flash, redirect, url_for, send_from_directory
from app import app
from app.forms import LoginForm, RegistrationForm, PostForm
from app.models import User, Post
from app import db
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.sql import select
from werkzeug.utils import secure_filename
import os


@app.errorhandler(404)
def not_found_err(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def not_found_err(error):
    return render_template('500.html'), 500


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Richard'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

def dict_from_obj(p):
    d = dict((key, value) for key, value in p.__dict__.items()
        if not callable(value) and not key.startswith('_'))
    return d

@app.template_filter('e7formatdatetime')
def format_datetime(value, format="%d %b %Y %I:%M %p"):
    """Format a date time to (Default): d Mon YYYY HH:MM P"""
    if value is None:
        return ""
    return value.strftime(format)


@app.route('/board', methods=['GET', 'POST'])
@login_required
def board():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        # TODO: check this sanitizes message.
        flash('You posted {}'.format(post.body))
        # redirect to clear form
        return redirect(url_for('board'))
    #posts = Post.query.all()
    s = select([User,Post]).where(Post.user_id == User.id)
    results = db.session.execute(s)
    posts = []
    for row in results:
        u = row[0]
        p = row[1]
        post = dict_from_obj(p)
        post['username'] = u.username
        posts.append(post)
    return render_template('board.html', title='Message Board', form=form, posts=posts)
        
# TODO: validate file contents as actual image.

# TODO: include images as:
# url_for('static', filename='avatars/' + str(user_id))

@app.route('/uploads/<filename>')
@login_required
def upload(filename):
    # TODO: This should be absolute, probably
    root_dir = os.getcwd()
    #print("root_dir is", root_dir)  # TODO:
    return send_from_directory(os.path.join(root_dir, app.config['UPLOAD_PATH']), filename)

@app.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    uploaded_file = request.files['file']
    filename = uploaded_file.filename
    print('your filename was', filename) # TODO: real log

    filename = secure_filename(filename)
    print("filename is", filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        print("file_ext is", file_ext)
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        save_path = os.path.join(app.config['UPLOAD_PATH'], filename)
        # TODO: real logging
        print("Saving uploaded file to", filename)
        flash('Your image was uploaded to {}'.format(url_for('upload', filename=filename)))
        # TODO: save images into database as a message post as well.
        
        uploaded_file.save(save_path)

    return redirect(url_for('board'))
