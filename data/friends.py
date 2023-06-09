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
    answer = sqlalchemy.Column(sqlalchemy.Boolean, default=None)
    time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def serialize(self, answ=True):
        data = SerializerMixin.to_dict(self)
        if not answ:
            del data['answer']
        return data


class Friends(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'friends'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    request_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('study_requests.id'))
    student_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    teacher_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))

    def serialize(self):
        data = SerializerMixin.to_dict(self)
        del data['request_id']
        return data
