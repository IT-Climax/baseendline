from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from ..core import db


class ParticipantClass(db.Model):
    __tablename__ = 'participant_classes'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)  # E.g., "Livestock Farming"
    description = Column(Text, nullable=True)

    questions = relationship('FGDQuestion', back_populates='participant_class')


class FGDQuestion(db.Model):
    __tablename__ = 'fgd_questions'
    id = Column(Integer, primary_key=True)
    participant_class_id = Column(Integer, ForeignKey('participant_classes.id'), nullable=False)
    question_text = Column(Text, nullable=False)
    question_order = Column(Integer, nullable=False)  # To order questions in the app
    question_type = Column(String(20), nullable=False)  # 'text', 'multiple_choice', 'rating', etc.
    is_required = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    participant_class = relationship('ParticipantClass', back_populates='questions')
    options = relationship('FGDQuestionOption', back_populates='question', cascade='all, delete-orphan')


class FGDQuestionOption(db.Model):
    __tablename__ = 'fgd_question_options'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('fgd_questions.id'), nullable=False)
    option_text = Column(String(255), nullable=False)
    option_order = Column(Integer, nullable=False)  # To order options

    question = relationship('FGDQuestion', back_populates='options')


class FGDParticipant(db.Model):
    __tablename__ = 'fgd_participants'
    id = Column(Integer, primary_key=True)
    participant_class_id = Column(Integer, ForeignKey('participant_classes.id'), nullable=False)
    name = Column(String(150), nullable=False)
    gender = Column(String(20), nullable=True)
    age = Column(Integer, nullable=True)
    contact_info = Column(String(255), nullable=True)  # Optional contact info
    created_at = Column(DateTime, default=datetime.utcnow)

    participant_class = relationship('ParticipantClass')
    answers = relationship('FGDAnswer', back_populates='participant', cascade='all, delete-orphan')


class FGDAnswer(db.Model):
    __tablename__ = 'fgd_answers'
    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, ForeignKey('fgd_participants.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('fgd_questions.id'), nullable=False)
    selected_option_id = Column(Integer, ForeignKey('fgd_question_options.id'), nullable=True)
    answer_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    participant = relationship('FGDParticipant', back_populates='answers')
    question = relationship('FGDQuestion')
    selected_option = relationship('FGDQuestionOption')
