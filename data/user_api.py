from io import BytesIO

from flask import jsonify
from flask_restful import Resource

from .db_session import *
from .scores import *
from .user import *
from .friends import *
from flask import Blueprint
from flask_restful import Api

users_api = Blueprint("users", __name__)
api = Api(users_api)


class UsersListResource(Resource):
    def get(self):
        db = create_session()
        users = db.query(User).all()
        return jsonify(*[user.serialize() for user in users])


class StudentsListResource(Resource):
    def get(self):
        db = create_session()
        students = db.query(User).filter(User.role == "student").all()
        return jsonify([student.serialize() for student in students])


class TeachersListResource(Resource):
    def get(self):
        db = create_session()
        teachers = db.query(User).filter(User.role == "teacher").all()
        return jsonify([teacher.serialize() for teacher in teachers])


class FriendRequestsListResource(Resource):
    def get(self, user_id):
        db = create_session()
        friend_requests = db.query(Requestions).filter(Requestions.teacher_id == user_id).all()
        return jsonify([fr.serialize(answ=False) for fr in friend_requests])


class AcceptedFriendRequestsListResource(Resource):
    def get(self, user_id):
        db = create_session()
        try:
            if db.query(User).filter(User.id == user_id).first().role == 'teacher':
                accepted_requests = db.query(Requestions).filter(
                    Requestions.answer == True, Requestions.teacher_id == user_id).all()
            else:
                accepted_requests = db.query(Requestions).filter(
                    Requestions.answer == True, Requestions.student_id == user_id).all()
        except:
            return jsonify("Пользователь с таким id не найден")
        return jsonify([req.serialize() for req in accepted_requests])


class DeclinedFriendRequestsListResource(Resource):
    def get(self, user_id):
        db = create_session()
        try:
            if db.query(User).filter(User.id == user_id).first().role == 'teacher':
                declined_requests = db.query(Requestions).filter(Requestions.answer == False
                                                                 , Requestions.teacher_id == user_id).all()
            else:
                declined_requests = db.query(Requestions).filter(Requestions.answer == False
                                                                 , Requestions.student_id == user_id).all()
        except:
            return jsonify("Пользователь с таким id не найден")
        return jsonify([req.serialize() for req in declined_requests])


class FriendsListResource(Resource):
    def get(self, user_id):
        db = create_session()
        try:
            if db.query(User).filter(User.id == user_id).first().role == 'teacher':
                friends = db.query(Friends).filter(Friends.teacher_id == user_id).all()
            else:
                friends = db.query(Friends).filter(Friends.student_id == user_id).all()
        except:
            return jsonify("Пользователь с таким id не найден")
        return jsonify([friend.serialize() for friend in friends])


api.add_resource(UsersListResource, "/")
api.add_resource(StudentsListResource, "/students")
api.add_resource(TeachersListResource, "/teachers")
api.add_resource(FriendRequestsListResource, "/<int:user_id>/friend_requests")
api.add_resource(AcceptedFriendRequestsListResource, "/<int:user_id>/friend_requests/accepted")
api.add_resource(DeclinedFriendRequestsListResource, "/<int:user_id>/friend_requests/declined")
api.add_resource(FriendsListResource, "/<int:user_id>/friends/")
