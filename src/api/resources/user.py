from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from ...db.models.model import User, RoleEnum, Enumerator, Participant
from ...db.core import db
from ...utils.auth import role_required

# Parser for user update
user_parser = reqparse.RequestParser()
user_parser.add_argument('first_name', type=str)
user_parser.add_argument('middle_name', type=str)
user_parser.add_argument('last_name', type=str)
user_parser.add_argument('email', type=str)
user_parser.add_argument('gender', type=str, choices=('Male', 'Female', '0'))
user_parser.add_argument('password', type=str)


class UserListResource(Resource):
    @jwt_required()
    @role_required('ADMIN', 'SUPER_ADMIN')
    def get(self):
        users = User.query.all()
        total = len(users)
        user_list = []
        for user in users:
            user_info = {
                'id': user.id,
                'First_name': user.first_name,
                'Last_name': user.last_name,
                'Email': user.email,
                'Gender': user.gender.name,
                'Role': user.user_type.name
            }
            user_list.append(user_info)
        return {'Total': total, 'Users': user_list}, 200

    @jwt_required()
    @role_required('ADMIN', 'SUPER_ADMIN')
    def post(self):
        # Reuse the register resource logic
        from ..resources.auth import register_parser
        args = register_parser.parse_args()

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

        return {'message': 'User created successfully', 'user_id': user.id}, 201


class UserResource(Resource):
    @jwt_required()
    def get(self, user_id):
        # Get current user identity
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # If not admin and not accessing own profile, return 403
        if (current_user.user_type == RoleEnum.ENUMERATOR and
                int(current_user_id) != int(user_id)):
            return {'message': 'Access forbidden'}, 403

        user = User.query.get_or_404(user_id)
        # participant = Participant.query.filter_by(Participant.user_id==user_id).all()
        # total_participants = len(participant)

        return {
            'id': user.id,
            'first_name': user.first_name,
            'middle_name': user.middle_name,
            'last_name': user.last_name,
            'email': user.email,
            'gender': user.gender.name,
            'user_type': user.user_type.name,
            "Participant": {
                "Total" : "total_participants"
            }
        }

    @jwt_required()
    @role_required('ADMIN', 'SUPER_ADMIN')
    def put(self, user_id):
        user = User.query.get_or_404(user_id)
        args = user_parser.parse_args()

        if args.get('first_name'):
            user.first_name = args['first_name']
        if args.get('middle_name'):
            user.middle_name = args['middle_name']
        if args.get('last_name'):
            user.last_name = args['last_name']
        if args.get('email'):
            if User.query.filter_by(email=args['email']).first() and user.email != args['email']:
                return {'message': 'Email already in use'}, 400
            user.email = args['email']
        if args.get('gender'):
            user.gender = args['gender']
        if args.get('password'):
            user.password = generate_password_hash(args['password'])

        db.session.commit()

        return {'message': 'User updated successfully'}

    @jwt_required()
    @role_required('SUPER_ADMIN')
    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        participant_count = Participant.query.filter_by(user_id=user.id).count()
        if participant_count > 0:
            return {
                       'message': 'Unable to delete user: user has registered participants.'
                   }, 400
        db.session.delete(user)
        db.session.commit()

        return {'message': 'User deleted successfully'}
