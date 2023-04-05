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


class SettingsForm(FlaskForm):
    school_subject_1 = SelectField('Предмет 2',
                        choices=[('English', "Английский"), ('Biology', 'Биология'),
                                 ('Geography', 'География'), ('History', 'История'),
                                 ('literature', 'Литература'), ('Math', 'Математика профиль'),
                                 ('Social Science', 'Обществознание'), ('Russian', 'Русский язык'),
                                 ('Physics', 'Физика'), ('Chemistry', 'Химия')], validators=[DataRequired()])

    school_subject_2 = SelectField('Предмет 2',
                       choices=[('English', "Английский"), ('Biology', 'Биология'),
                                ('Geography', 'География'), ('History', 'История'),
                                ('literature', 'Литература'), ('Math', 'Математика профиль'),
                                ('Social Science', 'Обществознание'), ('Russian', 'Русский язык'),
                                ('Physics', 'Физика'), ('Chemistry', 'Химия')], validators=[DataRequired()])

    confirm_password = StringField('Смена пароля', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Подтвердить пароль')
    submit2 = SubmitField('Подтвердить предметы')


class LoginForm(FlaskForm):
    username = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')