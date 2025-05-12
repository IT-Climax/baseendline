
from flask import Blueprint, request, jsonify
from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from ...db.models.model import User, RoleEnum
from ...db.core import db
from ...utils.auth import role_required

register_parser = reqparse.RequestParser()
register_parser.add_argument('first_name', type=str, required=True, help='First name is required')
register_parser.add_argument('last_name', type=str, required=True, help='Last name is required')
register_parser.add_argument('middle_name', type=str)
register_parser.add_argument('email', type=str, required=True, help='Email is required')
register_parser.add_argument('password', type=str, required=True, help='Password is required')
register_parser.add_argument('gender', type=str, choices=('Male', 'Female', 'Undisclosed'), default='Undisclosed')
register_parser.add_argument('user_type', type=str, choices=('OBSERVER', 'ENUMERATOR', 'ADMIN', 'SUPER_ADMIN'),
                             default='ENUMERATOR')

login_parser = reqparse.RequestParser()
login_parser.add_argument('email', type=str, required=True, help='Email is required')
login_parser.add_argument('password', type=str, required=True, help='Password is required')


class RegisterResource(Resource):
    """Resource for user registration."""

    # @jwt_required()
    # @role_required('ADMIN', 'SUPER_ADMIN')
    def post(self):
        args = register_parser.parse_args()  # Use request parser for validation

        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already registered'}, 400

        user = User(
            first_name=args['first_name'],
            middle_name=args['middle_name'],
            last_name=args['last_name'],
            email=args['email'],
            gender=args['gender'],
            password=generate_password_hash(args['password']),
            user_type=RoleEnum[args['user_type']]
        )
        db.session.add(user)
        db.session.commit()
        return {'message': 'User registered successfully', 'user_id': user.id}, 201


class LoginResource(Resource):

    def post(self):
        args = login_parser.parse_args()
        user = User.query.filter_by(email=args['email']).first()
        if not user or not check_password_hash(user.password, args['password']):
            return {'message': 'Invalid credentials'}, 401

        access_token = create_access_token(identity=user.id)

        return {
                   'access_token': access_token,
                   'user_id': user.id,
                   'user_type': user.user_type.name
               }, 200


class ProfileResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        return {
            'id': user.id,
            'first_name': user.first_name,
            'middle_name': user.middle_name,
            'last_name': user.last_name,
            'email': user.email,
            'gender': user.gender.name if hasattr(user.gender, 'name') else user.gender,
            'user_type': user.user_type.name
        }


# Change my password as a successful login user
class ChangePassword(Resource):
    reset_parser = reqparse.RequestParser()
    reset_parser.add_argument('old_password', type=str, required=True, help='Confirm old password')
    reset_parser.add_argument('new password', type=str, required=True, help='Set new Password')

    @jwt_required()
    def post(self):
        args = self.reset_parser.parse_args()
        user_id = get_jwt_identity()
        data = request.get_json()
        old_password = args['old_password']
        new_password = args['new_password']
        user = User.query.get(user_id)
        if not user or not check_password_hash(user.password, old_password):
            return {'msg': 'Incorrect Old Password'}, 400
        user.password = generate_password_hash(new_password)
        db.session.commit()
        return {'msg': 'Password updated successfully'}


