from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from .user import User


class RegistrationForm(FlaskForm):
    username = StringField('ФИО', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердить пароль', validators=[DataRequired()])
    role = SelectField('Роль',
                  choices=[('teacher', "Учитель"), ('student', 'Ученик')], validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    username = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')