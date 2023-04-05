from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

from data import db_session
from data.user import User
from data.forms import *
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'

@app.route('/')
def index():
    return render_template('index.html', title='ЕГЭпасс')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        db = db_session.create_session()
        print(str(form.password.data), str(form.confirm_password.data), str(form.password.data) != str(form.confirm_password.data))
        if str(form.password.data) != str(form.confirm_password.data):
            flash("Вы не подтвердили пароль", "Ошибка")
        elif db.query(User).filter(User.email == form.email.data).first():
            flash("Пользователь уже занят", "Ошибка")
        else:
            user = User(email=form.email.data, username=form.username.data, role=form.role.data)
            user.set_password(form.password.data)
            db.add(user)
            db.commit()
            return redirect(url_for("login"))
    return render_template("register.html", title="Регистрация", form=form)


@app.route('/settings', methods=['GET', 'POST'])
def setting():
    form = SettingsForm()
    if form.validate_on_submit():
        if str(form.school_subject_1.data) == str(form.school_subject_2.data):
            flash("Одинаковые предметы по выбору", "Ошибка")
        #  Тут Потом с паролем делать
    return render_template("settings.html", title="Настройки", form=form)


@app.route('/login')
def login():
    return "Это страница входа"


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@login_manager.user_loader
def load_user(user):
    return User.query.get(int(user))


def main():
    db_session.global_init("database.db")
    app.run()


if __name__ == '__main__':
    main()