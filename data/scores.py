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
    "физика": [1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 1, 1, 1, 2, 2, 2, 1, 2, 2, 2, 1, 1, 3, 2, 2, 3, 3, 3, 4],
    "биология": [1, 2, 1, 1, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3],
    "история": [2, 1, 2, 3, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 2, 3, 3],
    "обществознание": [1, 2, 1, 2, 2, 2, 2, 2, 1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 4, 3, 4, 6],
    "химия": [1, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 2, 2, 4, 5, 3, 4],
    "информатика": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2]
}
primary_to_secondary = {"математика (профильный)": {
    1: 6, 2: 11, 3: 17, 4: 22, 5: 27, 6: 34, 7: 40, 8: 46, 9: 52, 10: 58, 11: 64, 12: 66, 13: 68, 14: 70, 15: 72,
    16: 74, 17: 76, 18: 78,
    19: 80, 20: 82, 21: 84, 22: 86, 23: 88, 24: 90, 25: 92, 26: 94, 27: 96, 28: 98, 29: 100, 30: 100, 31: 100},
    "русский язык": {1: 3, 2: 5, 3: 8, 4: 10, 5: 12, 6: 15, 7: 17, 8: 20, 9: 22, 10: 24, 11: 26, 12: 28, 13: 30, 14: 32,
                     15: 34, 16: 36, 17: 38, 18: 39, 19: 40, 20: 41, 21: 43, 22: 44, 23: 45, 24: 46, 25: 48, 26: 49,
                     27: 50, 28: 51, 29: 53, 30: 54, 31: 55, 32: 56, 33: 57, 34: 59, 35: 60, 36: 61, 37: 62, 38: 64,
                     39: 65, 40: 66, 41: 67, 42: 69, 43: 70, 44: 71, 45: 72, 46: 73, 47: 76, 48: 78, 49: 80, 50: 82,
                     51: 85, 52: 87, 53: 89, 54: 91, 55: 94, 56: 96, 57: 98, 58: 100}}


# Таблица добавления результатов теста
class TestSeparately(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'separately_tests'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    exam_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("exams.id"))
    task_number = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    score = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    subject = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("exams.subject"), nullable=True)


class Exams(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'exams'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    subject = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    primary_score = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    secondary_score = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
