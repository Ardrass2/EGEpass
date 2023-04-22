from flask_login import UserMixin
import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from .user import User


class Requestions(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'study_requests'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    student_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    teacher_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    answer = sqlalchemy.Column(sqlalchemy.BOOLEAN)
    time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)


class Friends(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'friends'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    request_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('study_requests.id'))
    student_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    teacher_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
