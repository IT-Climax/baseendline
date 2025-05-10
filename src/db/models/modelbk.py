from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import relationship, backref
from ..core import db
from enum import Enum
from sqlalchemy.orm import declarative_base
Base = declarative_base()


class RoleEnum(Enum):
    OBSERVER = 0
    ENUMERATOR = 1
    ADMIN = 2
    SUPER_ADMIN = 3


class GenderEnum(Enum):
    Male = 'MALE'
    Female = 'FEMALE'
    Undisclosed = 'UNDISCLOSED'


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    middle_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    gender = db.Column(db.Enum(GenderEnum), nullable=True)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=True)
    user_type = db.Column(db.Enum(RoleEnum), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())

    enumerator = relationship('Enumerator', uselist=False, back_populates='user')
    participant = relationship('Participant', uselist=False, back_populates='user')


class Participant(db.Model):
    __tablename__ = 'participants'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    age = db.Column(db.Integer, nullable=False)
    nin = db.Column(db.String(255), nullable=True)
    marital_status = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    education = db.Column(db.String(255), nullable=False)
    submitted_at = db.Column(db.String(255), nullable=False)
    highest_formal_education = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255))
    coordinates = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())

    user = relationship('User', back_populates='participant')
    answers = relationship('QuestionAnswer', back_populates='participant')


class Enumerator(db.Model):
    __tablename__ = 'enumerators'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    photo_url = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(255), default="active")
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())

    user = relationship('User', back_populates='enumerator')
    answers = relationship('QuestionAnswer', back_populates='enumerator')


class Section(db.Model):
    __tablename__ = 'sections'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())
    questions = relationship('QuestionBase', back_populates='section')


class QuestionPhase(db.Model):
    __tablename__ = 'question_phase'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())
    questions = relationship('QuestionBase', back_populates='phase')


class QuestionBase(db.Model):
    __tablename__ = 'question_base'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(45), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'))
    parent_question_id = db.Column(db.Integer, db.ForeignKey('question_base.id'), nullable=True)
    phase_id = db.Column(db.Integer, db.ForeignKey('question_phase.id'))
    is_required = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    tags = db.Column(db.String(255))
    help_text = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())

    section = relationship('Section', back_populates='questions')
    phase = relationship('QuestionPhase', back_populates='questions')
    options = relationship('QuestionOptions', back_populates='question')
    parent = relationship('QuestionBase', remote_side=[id], backref='children')
    options = db.relationship('QuestionOptions', back_populates='question', lazy=True,
                              foreign_keys='QuestionOptions.question_id')


class QuestionOptions(db.Model):
    __tablename__ = 'question_options'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question_base.id'), nullable=False)
    follow_up_question_id = db.Column(db.Integer, db.ForeignKey('question_base.id'), nullable=True)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())

    question = db.relationship(
        'QuestionBase',
        back_populates='options',
        foreign_keys=[question_id]
    )
    follow_up = db.relationship(
        'QuestionBase',
        foreign_keys=[follow_up_question_id]
    )


class QuestionAnswer(db.Model):
    __tablename__ = 'question_answer'
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    enumerator_id = db.Column(db.Integer, db.ForeignKey('enumerators.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question_base.id'), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())

    participant = relationship('Participant', back_populates='answers')
    enumerator = relationship('Enumerator', back_populates='answers')
    question = relationship('QuestionBase')
    selected_options = relationship('AnswerOptionSelected', back_populates='answer')


class AnswerOptionSelected(db.Model):
    __tablename__ = 'answer_option_selected'
    id = db.Column(db.Integer, primary_key=True)
    question_answer_id = db.Column(db.Integer, db.ForeignKey('question_answer.id'))
    option_id = db.Column(db.Integer, db.ForeignKey('question_options.id'))

    answer = relationship('QuestionAnswer', back_populates='selected_options')
    option = relationship('QuestionOptions')