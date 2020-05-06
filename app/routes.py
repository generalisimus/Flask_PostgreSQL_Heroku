from datetime import datetime

from flask import render_template, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import redirect

from app import app, login_manager, bcrypt, db
from flask import abort
from .models import User, Tasks
from .forms import UserForm, TasksForm
from flask_login import LoginManager, login_required


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


@app.route('/')
def home_page():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.get(form.email.data)
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=True)
            return redirect('/')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def create_user():
    form = UserForm()
    if form.validate_on_submit():
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        test_user = User.query.get(email)
        if test_user:
            abort(409)
        user = User(name = name, email=email, password=bcrypt.generate_password_hash(password).decode('utf-8'))
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/add-tasks', methods=['GET', 'POST'])
@login_required
def add_tasks():
    form = TasksForm()
    if form.validate_on_submit():
        title = request.form.get('title')
        description = request.form.get('description')
        time_start = request.form.get('time_start')
        time_end = request.form.get('time_end')
        if (time_end <= time_start) or (datetime.strptime(time_end, '%Y-%m-%dT%H:%M') <= datetime.now()):
            message = 'Wrong event time!'
            return render_template('add-tasks.html', form=form, message=message)
        tasks = Tasks(author=current_user.email, title=title, description=description, time_start=time_start, time_end=time_end)
        db.session.add(tasks)
        db.session.commit()
        return redirect('/')
    return render_template('add-tasks.html', form=form)


@app.route('/tasks-list')
@login_required
def tasks_list():
    tasks = Tasks.query.all()
    for task in tasks:
        if datetime.now() >= task.time_end:
            db.session.delete(task)
            db.session.commit()
    return render_template('tasks-list.html', tasks=tasks)


@app.route('/tasks-detail/<int:tasks_id>', methods=['GET', 'POST'])
@login_required
def tasks_detail(tasks_id):
    tasks = Tasks.query.get(tasks_id)
    form = TasksForm()
    if tasks:
        if current_user.is_authenticated:
            if tasks.author == current_user.email:
                if form.validate_on_submit():
                    title = request.form.get('title')
                    desc = request.form.get('descruption')
                    time_start = request.form.get('time_start')
                    time_end = request.form.get('time_end')
                    if (time_end <= time_start) or (datetime.strptime(time_end, '%Y-%m-%dT%H:%M') <= datetime.now()):
                        message = 'Wrong event time!'
                        return render_template('tasks-detail.html', tasks=tasks, form=form, message=message)
                    tasks.title = title
                    tasks.desc = desc
                    tasks.time_start = time_start
                    tasks.time_end = time_end
                    db.session.commit()
                    return redirect('/')
        return render_template('tasks-detail.html', tasks=tasks, form=form)
    return abort(404)
