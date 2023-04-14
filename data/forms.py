from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, Email, NumberRange
from .user import User


class RegistrationForm(FlaskForm):
    username = StringField('ФИО', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердить пароль', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Роль', choices=[('teacher', "Учитель"), ('student', 'Ученик')], validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class SettingsForm(FlaskForm):
    change_password = PasswordField('Новый пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердить пароль',
                                     validators=[DataRequired(), Length(min=6), EqualTo(change_password)])
    submit_pass = SubmitField('Подтвердить изменения')


class TeacherForm(FlaskForm):
    user_needed = StringField('Имя ученика, покашта', validators=[DataRequired()])
    submit_user = SubmitField('ТАКТОЧНА')


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')
