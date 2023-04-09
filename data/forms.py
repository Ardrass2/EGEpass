from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from .user import User


class AdditionResultsForm(FlaskForm):
    checkboxes_fields = [BooleanField(f"{i}") for i in range(40)]
    numb_fields = [IntegerField(f"{i}", default=0) for i in range(50)]
    submit = SubmitField('Отправить результат')


class RegistrationForm(FlaskForm):
    username = StringField('ФИО', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердить пароль', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Роль', choices=[('teacher', "Учитель"), ('student', 'Ученик')], validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class SettingsForm(FlaskForm):
    change_password = PasswordField('Новый пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердить пароль', validators=[DataRequired(), Length(min=6)])
    submit_pass = SubmitField('Подтвердить изменения')


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')
