from flask import Blueprint
from flask_restful import Api
from .auth import RegisterResource, LoginResource, ProfileResource, ChangePassword
from .sections import SectionListResource, SectionResource
# from .sections import sections_bp
from .user import UserResource, UserListResource
from .participant import ParticipantRegistrationResource, ParticipantQuestionsResource, ParticipantAnswerResource
from .fgdquestions import FGDQuestionsFileUploadResource, FGDQuestionUpdateResource, FGDQuestionsDeleteAllResource, \
    FGDQuestionsResource, FGDSubmitAnswersResource
from .enumeratorReport import EnumeratorDailyReportResource

# Create blueprint for auth routes
bp = Blueprint('auth', __name__, url_prefix='/api')
api = Api(bp)


# Authentication
api.add_resource(RegisterResource, '/auth/register')
api.add_resource(LoginResource, '/auth/login')
api.add_resource(ProfileResource, '/auth/me')
api.add_resource(ChangePassword, '/auth/change-password')
# Reset password

# Sections
api.add_resource(SectionListResource, '/sections')
api.add_resource(SectionResource, '/section/<int:section_id>')


# users
api.add_resource(UserListResource, '/users')
api.add_resource(UserResource, '/user/<int:user_id>')

# participants
api.add_resource(ParticipantRegistrationResource, '/participant/register')
api.add_resource(ParticipantQuestionsResource, '/participant/questions')
api.add_resource(ParticipantAnswerResource, '/participant/answers')

api.add_resource(FGDQuestionsFileUploadResource, '/upload-fgd')
api.add_resource(FGDQuestionUpdateResource, '/fgd-question/<int:question_id>')
api.add_resource(FGDQuestionsDeleteAllResource, '/delete-all-fgd')
api.add_resource(FGDQuestionsResource, '/fgd-get-questions/<int:participant_class_id>')
api.add_resource(FGDSubmitAnswersResource, '/fgd-response')

# Enumerator Report
api.add_resource(EnumeratorDailyReportResource, '/report-enumerator')


def init_app(app):
    """Register the blueprint with the Flask app."""
    app.register_blueprint(bp)
    print("Blueprint Registered")

