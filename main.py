from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import plotly.graph_objs as go
import plotly.express as px
import plotly
import json
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
        if request.method == 'POST':
            all_score = []
            for i in range(len(subject_tasks[subject])):
                if subject_tasks[subject][i] == 1:
                    all_score.append(1 if request.form.get(f'task_{i + 1}') == 'on' else 0)
                else:
                    all_score.append(
                        int(request.form.get(f'integer_{i + 1}')) if request.form.get(f'integer_{i + 1}') else 0)
            db = db_session.create_session()
            exam = Exams(user_id=current_user.id, subject=subject, primary_score=sum(all_score))
            db.add(exam)
            for i, score in enumerate(all_score):
                scores = TestSeparately(user_id=current_user.id, exam_id=exam.id, task_number=i + 1, score=score,
                                        subject=exam.subject)
                db.add(scores)
            db.commit()
            return redirect(url_for(f"subjects"))
    else:
        return redirect(url_for("login"))
    if subject in subject_tasks.keys():
        return render_template("add_result.html", subject=subject, tasks=subject_tasks[subject],
                               enumerate=enumerate, title=subject.capitalize())


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('add_result'))
    form = RegistrationForm()
    if form.validate_on_submit():
        db = db_session.create_session()
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
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
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


@app.route("/subjects/<subject>")
def subject(subject):
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        db = db_session.create_session()
        exams = db.query(Exams).filter(Exams.subject == subject).all()
        if exams:
            scores = [exam.primary_score for exam in exams]
            number = list(range(1, len(exams) + 1))

            fig = px.line(x=number, y=scores, labels={'x': 'Номер пробника', 'y': 'Количество баллов'},
                          title='Первичные баллы')
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        else:
            return render_template("subject.html", title=subject, subject=subject, graphJSON=0)

    return render_template("subject.html", title=subject, subject=subject, graphJSON=graphJSON)


@app.route("/subjects")
def subjects():
    if not current_user.is_authenticated:
        return redirect(url_for("index"))
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
