from dns.serial import Serial
from flask_login import UserMixin
import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from .user import User

subject_tasks = {
    "русский язык": [1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 24],
    "математика (базовый)": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    "математика (профильный)": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 2, 2, 3, 4, 4],
    "физика": [1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 1, 1, 1, 2, 2, 2, 1, 2, 2, 2, 1, 1, 3, 2, 2, 3, 3, 3, 4]
}


#Таблица добавления результатов теста
class TestSeparately(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'separately_tests'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    exam_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("exams.id"))
    task_number = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    score = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    subject = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("exams.subject"),nullable=True)


class Exams(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'exams'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    subject = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    primary_score = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    secondary_score = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
