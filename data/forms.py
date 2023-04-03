from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from .user import User


class RegistrationForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердить пароль', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Роль',
                  choices=[('Учитель', 'Учитель'), ('Ученик', 'Ученик')], validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    def validate_mail(self, mail):
        user = User.query.filter_by(email=mail.data).first()
        if user:
            raise ValidationError('Эта почта уже занята')


class LoginForm(FlaskForm):
    username = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')