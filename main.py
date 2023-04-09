from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from data.scores import subject_tasks, Exams, TestSeparately
from data import db_session
from data.user import User
from data.forms import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='ЕГЭпасс')


@app.route('/login', methods=['POST', 'GET'])
def login():
    db = db_session.create_session()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        elif user:
            flash("Неправильный логин либо пароль", "Ошибка")
        else:
            flash("Пользователь не найден. Необходима регистрация.", "Ошибка")
    return render_template("login.html", form=form, title='Вход')


@app.route('/add_result/<subject>', methods=['POST', 'GET'])
def add_result(subject):
    if current_user.is_authenticated:
        form = AdditionResultsForm()
        if subject.lower() in subject_tasks.keys():
            return render_template("add_result.html", subject=subject, tasks=subject_tasks[subject],
                                   enumerate=enumerate, form=form, title=subject.capitalize())
        if request.method == 'POST' and form.validate_on_submit():
            count = 0
            for field in form:
                pass

    else:
        return redirect(url_for("login"))
    return render_template("add_result.html", title=subject.capitalize())


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('add_result'))
    form = RegistrationForm()
    if form.validate_on_submit():
        db = db_session.create_session()
        print(str(form.password.data), str(form.confirm_password.data),
              str(form.password.data) != str(form.confirm_password.data))
        if str(form.password.data) != str(form.confirm_password.data):
            flash("Вы не подтвердили пароль", "Ошибка")
        elif db.query(User).filter(User.email == form.email.data).first():
            flash("Пользователь уже занят", "Ошибка")
        else:
            user = User(email=form.email.data, username=form.username.data, role=form.role.data)
            user.set_password(form.password.data)
            db.add(user)
            db.commit()
            login_user(user)
            return redirect(url_for("index"))
    return render_template("register.html", title="Регистрация", form=form)


@app.route('/settings', methods=['GET', 'POST'])
def setting():
    form = SettingsForm()
    if form.validate_on_submit():
        if not str(form.change_password.data) == str(form.confirm_password.data):
            flash("Пароли различаются", "Ошибка")
        else:
            db = db_session.create_session()
            current_user.hashed_password.replace(current_user.set_password(form.change_password.data))
            db.merge(current_user)
            db.commit()
    return render_template("settings.html", title="Настройки", form=form)


@app.route('/subjects/<subject>')
def subject(subject):
    return render_template("subject.html", title=subject, subject=subject)


@app.route("/subjects")
def subjects():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    return render_template("subjects.html", subjects=subject_tasks.keys(), title="Предметы")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@login_manager.user_loader
def load_user(user):
    db = db_session.create_session()
    return db.query(User).get(int(user))


def main():
    db_session.global_init("database.db")
    app.run()


if __name__ == '__main__':
    main()