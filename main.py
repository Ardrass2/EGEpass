from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import plotly.graph_objs as go
import plotly.express as px
import plotly
import json
from werkzeug.security import generate_password_hash
from data.scores import *
from data import db_session
from data.user import User
from data.forms import *
from data.date import *


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


@app.route('/subjects/<subject>/stats')
def stats(subject):
    if current_user.is_authenticated:
        db = db_session.create_session()
        all_exams = db.query(Exams).filter(Exams.subject == subject, Exams.user_id == current_user.id).all()
        all_secondary_results = []
        for exam in all_exams:
            all_secondary_results.append(exam.secondary_score)
        best = max(all_secondary_results) if all_secondary_results else 0
        worst = min(all_secondary_results) if all_secondary_results else 0
        all_average = get_all_tasks(subject) if all_secondary_results else []
    return render_template("stats.html", avg_score=round(
        sum(all_secondary_results) / len(all_secondary_results) if all_secondary_results else 0, 3), best_score=best,
                           worst_score=worst, all_tasks=all_average, len=len, round=round, title=subject.capitalize(),
                           subject_tasks=subject_tasks[subject], all_exams=all_exams)


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
            if subject != "математика (базовый)":
                exam = Exams(user_id=current_user.id, subject=subject, primary_score=sum(all_score),
                             secondary_score=primary_to_secondary[subject][sum(all_score)])
            else:
                exam = Exams(user_id=current_user.id, subject=subject, primary_score=sum(all_score))
            db.add(exam)
            db.commit()
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
            if str(form.change_password.data) == str(form.confirm_password.data):
                current_user.hashed_password.replace(current_user.set_password(form.change_password.data))
                current_user.hashed_password = generate_password_hash(str(form.change_password.data))
            if form.school:
                current_user.school = form.school
            db.merge(current_user)
            db.commit()
            flash("Успешно")
    return render_template("settings.html", title="Настройки", form=form)


@app.route("/user/<id>")
def users(id):
    db = db_session.create_session()
    user = db.query(User).filter(User.id == int(id)).first()
    if user.role == "teacher":
        role = "Учитель"
    else:
        role = "Ученик"
    return render_template("user.html", name=user.username, role=role, school=user.school)


@app.route("/subjects/<subject>")
def subject(subject):
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    elif current_user.role == 'teacher':
        form = TeacherForm()
        return render_template('teacher.html', title=subject, subject=subject, form=form)
    else:
        bad = []
        db = db_session.create_session()
        exams = db.query(Exams).filter(Exams.subject == subject, Exams.user_id == current_user.id).all()
        if exams:
            a = get_all_tasks(subject, sort=True)
            for elem in a:
                bad.append(f"{elem}({round(a[elem], 3)} баллов в среднем)")
                if len(bad) > 3:
                    break
            bad = "№" + ", №".join(bad)
            primary_scores = [exam.primary_score for exam in exams]
            secondary_scores = [exam.secondary_score for exam in exams]
            number = list(range(1, len(exams) + 1))

            fig = px.line(x=number, y=primary_scores, labels={'x': 'Номер пробника', 'y': 'Количество баллов'},
                          title='Первичные баллы')
            primaryJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            fig = px.line(x=number, y=secondary_scores, labels={'x': 'Номер пробника', 'y': 'Количество баллов'},
                          title='Вторичные баллы')
            seconderyJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        else:
            return render_template("subject.html", title=subject, subject=subject, primaryJSON=0, secondaryJSON=0,
                                   bad=bad)

    return render_template("subject.html", title=subject, subject=subject, primaryJSON=primaryJSON,
                           secondoryJSON=seconderyJSON, bad=bad)


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


def get_all_tasks(subject, sort=False):
    db = db_session.create_session()
    average_score = {}
    for i in range(1, len(subject_tasks[subject]) + 1):
        points_of_tasks = db.query(TestSeparately).filter(TestSeparately.subject == subject,
                                                          TestSeparately.user_id == current_user.id,
                                                          TestSeparately.task_number == i).all()
        summary = 0
        num_of_tasks = 0
        for task in points_of_tasks:
            summary += int(task.score)
            num_of_tasks += 1
        average_score[i] = summary / num_of_tasks
    if sort:
        return dict(sorted(average_score.items(), key=lambda item: item[1]))
    else:
        return average_score


def main():
    db_session.global_init("static/database.db")
    app.run()


if __name__ == '__main__':
    main()
