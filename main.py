from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import plotly.graph_objs as go
#import plotly.express as px
import plotly
import json
from werkzeug.security import generate_password_hash

from data.friends import *
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
    return render_template('index.html', title='ЕГЭпасс', id=str(current_user.id))


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
                           subject_tasks=subject_tasks[subject], all_exams=all_exams, id=str(current_user.id))


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
                               enumerate=enumerate, title=subject.capitalize(), id=str(current_user.id))


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
    else:
        form = SettingsForm()
        if request.method == "POST":
            db = db_session.create_session()
            if str(form.change_password.data) == str(form.confirm_password.data):
                current_user.hashed_password = generate_password_hash(str(form.change_password.data))
            if form.school:
                current_user.school = form.school.data
            db.merge(current_user)
            db.commit()
            flash("Успешно")
        return render_template("settings.html", title="Настройки", form=form, id=str(current_user.id))


@app.route("/user/<id>", methods=["GET", "POST"])
def users(id):
    if current_user.is_authenticated:
        db = db_session.create_session()
        user = db.query(User).filter(User.id == int(id)).first()
        form = AddFriend()
        is_request = False
        if user.role == "teacher":
            role = "Учитель"
        else:
            role = "Ученик"
        requestions = db.query(Requestions).filter(Requestions.teacher_id == current_user.id).all()
        if db.query(Requestions).filter(
                Requestions.student_id == current_user.id or Requestions.teacher_id == int(id)).first():
            is_request = True
        if request.method == "POST":
            if not is_request:
                friend = Requestions(student_id=current_user.id, teacher_id=int(id))
                db.add(friend)
                db.commit()
                flash("Отправлено")
            if current_user.id == int(id):
                for requezt in requestions:
                    student_id = find_user(requezt.student_id).id
                    request_id = db.query(Requestions).filter(Requestions.teacher_id == current_user.id,
                                                              Requestions.student_id == student_id).first()
                    friendship = Friends(request_id=request_id.id, student_id=student_id, teacher_id=current_user.id)
                    db.add(friendship)
                    db.commit()
        return render_template("user.html", name=user.username, role=role, school=user.school,
                               current_id=str(current_user.id), requestions=requestions,
                               id=str(id), current_user_role=current_user.role, form=form, is_request=is_request,
                               find_user=find_user)

@app.route("/subjects/<subject>")
def subject(subject):
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    elif current_user.role == 'teacher':
        form = TeacherForm()
        return render_template('teacher.html', title=subject, subject=subject, form=form, id=str(current_user.id))
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
                           secondoryJSON=seconderyJSON, bad=bad, id=str(current_user.id))


@app.route("/subjects")
def subjects():
    if not current_user.is_authenticated:
        return redirect(url_for("index"))
    return render_template("subjects.html", subjects=subject_tasks.keys(), title="Предметы", id=str(current_user.id))


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


def find_user(id):
    db = db_session.create_session()
    return db.query(User).filter(User.id == id).first()


def main():
    db_session.global_init("db/database.db")
    app.run()


if __name__ == '__main__':
    main()
