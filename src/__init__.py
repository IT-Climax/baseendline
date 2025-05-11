from flask import Flask
from .config import Config
from .db.core import db, jwt, migrate, cors, bcrypt
from .api.resources import init_app
from .db.models import RoleEnum, GenderEnum, User, Section, Participant, Enumerator, QuestionPhase, QuestionBase, QuestionOptions, QuestionAnswer, \
    AnswerOptionSelected
from .scripts.upload_education_question import upload_education_questions


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    # migrate = Migrate(app, db, render_as_batch=True)

    with app.app_context():
        db.create_all()
        jwt.init_app(app)
        cors.init_app(app, resources={r"/*": {"origins": "*"}})
        bcrypt.init_app(app)
        init_app(app)
        # # Upload Questions
        upload_education_questions()


    @app.route('/')
    def home():
        return {'message': 'Survey in Class API Running'}

    return app
