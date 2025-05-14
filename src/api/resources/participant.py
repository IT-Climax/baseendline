from flask import Blueprint, request
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...db.core import db
from ...db.models.model import (
    User, RoleEnum, Participant, QuestionBase, QuestionOptions, QuestionPhase,
    QuestionAnswer, Section
)
from ...utils.auth import role_required
from datetime import datetime
from sqlalchemy.orm import joinedload


class ParticipantRegistrationResource(Resource):
    @jwt_required()
    @role_required('ENUMERATOR', 'ADMIN', 'SUPER_ADMIN')
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('age', type=int, required=True, help="Age is required")
        parser.add_argument('marital_status', type=str, required=True, help="Marital status is required")
        parser.add_argument('location', type=str, required=True, help="Location is required")
        parser.add_argument('education', type=str, required=True, help="Select one")
        parser.add_argument('highest_edu', type=str, required=True, help="Highest level of education is required")
        parser.add_argument('coordinate', type=str)
        parser.add_argument('nin', type=str)
        parser.add_argument('gender', type=str, required=True, help="Gender is required")
        args = parser.parse_args()

        user_id = get_jwt_identity()
        participant = Participant(
            user_id=user_id,
            age=args['age'],
            marital_status=args['marital_status'],
            location=args['location'],
            education=args['education'],
            highest_formal_education=args['highest_edu'],
            coordinates=args.get('coordinate'),
            nin=args.get('nin'),
            status=args.get('gender'),
            submitted_at=datetime.utcnow().isoformat()
        )
        db.session.add(participant)
        db.session.commit()
        return {'message': 'Participant registered', 'participant_id': participant.id}, 201


class ParticipantQuestionsResource(Resource):
    @jwt_required()
    @role_required('ENUMERATOR', 'ADMIN', 'SUPER_ADMIN')
    def get(self):
        """
        Load all questions for a selected phase (baseline or endline) with flow logic.
        Query param: ?phase=Baseline or ?phase=Endline
        """
        phase_name = request.args.get('phase', 'Baseline')
        phase = QuestionPhase.query.filter_by(title=phase_name).first()
        if not phase:
            return {'message': f'Phase {phase_name} not found'}, 404

        # Get all sections
        sections = Section.query.all()
        result = []

        for section in sections:
            root_questions = QuestionBase.query.filter_by(
                section_id=section.id,
                phase_id=phase.id,
                parent_question_id=None
            ).order_by(QuestionBase.display_order).all()
            if not root_questions:
                continue

            section_data = {
                'section_id': section.id,
                'section_title': section.title,
                'questions': []
            }
            for root_q in root_questions:
                q_data = self._process_question_with_children(root_q)
                section_data['questions'].append(q_data)
            result.append(section_data)

        return {
            'phase': phase_name,
            'sections': result
        }, 200

    def _process_question_with_children(self, question):
        options = []
        for opt in QuestionOptions.query.filter_by(question_id=question.id).all():
            opt_data = {
                'id': opt.id,
                'title': opt.title,
                'follow_up_question_id': opt.follow_up_question_id,
                'follow_up': None
            }
            if opt.follow_up_question_id:
                follow_up_q = QuestionBase.query.get(opt.follow_up_question_id)
                if follow_up_q:
                    opt_data['follow_up'] = self._process_question_with_children(follow_up_q)
            options.append(opt_data)
        return {
            'id': question.id,
            'title': question.title,
            'type': question.type,
            'is_required': question.is_required,
            'tags': question.tags,
            'options': options
        }


class ParticipantPhaseQuestionsResource(Resource):
    @jwt_required()
    @role_required('ENUMERATOR', 'ADMIN', 'SUPER_ADMIN')
    def get(self):
        """
        Load all questions for a selected phase (Baseline or Endline) with flow logic.
        Query param: ?phase=Baseline or ?phase=Endline (case-insensitive)
        """
        phase_name = request.args.get('phase', 'Baseline').strip().title()
        phase = QuestionPhase.query.filter_by(title=phase_name).first()
        if not phase:
            return {'message': f'Phase "{phase_name}" not found'}, 404

        # Get all sections
        sections = Section.query.all()
        result = []

        for section in sections:
            root_questions = QuestionBase.query.options(
                joinedload(QuestionBase.options).joinedload(QuestionOptions.follow_up)
            ).filter_by(
                section_id=section.id,
                phase_id=phase.id,
                parent_question_id=None
            ).order_by(QuestionBase.display_order).all()

            if not root_questions:
                continue

            section_data = {
                'section_id': section.id,
                'section_title': section.title,
                'questions': []
            }
            for root_q in root_questions:
                q_data = self._process_question_with_children(root_q)
                section_data['questions'].append(q_data)
            result.append(section_data)

        return {
            'phase': phase_name,
            'sections': result
        }, 200

    def _process_question_with_children(self, question, visited=None):
        if visited is None:
            visited = set()
        if question.id in visited:
            # Prevent infinite recursion
            return {
                'id': question.id,
                'title': question.title,
                'type': question.type,
                'is_required': question.is_required,
                'tags': question.tags,
                'options': []
            }
        visited.add(question.id)

        options = []
        for opt in question.options:
            opt_data = {
                'id': opt.id,
                'title': opt.title,
                'follow_up_question_id': opt.follow_up_question_id,
                'follow_up': None
            }
            if opt.follow_up_question_id and opt.follow_up:
                opt_data['follow_up'] = self._process_question_with_children(opt.follow_up, visited)
            options.append(opt_data)

        return {
            'id': question.id,
            'title': question.title,
            'type': question.type,
            'is_required': question.is_required,
            'tags': question.tags,
            'options': options
        }

class ParticipantAnswerResource(Resource):
    @jwt_required()
    @role_required('ENUMERATOR', 'ADMIN', 'SUPER_ADMIN')
    def post(self):
        """
        Submit participant answers. Accepts a list of answers for batch sync.
        Payload:
        {
            "participant_id": 123,
            "answers": [
                {
                    "question_id": 1,
                    "answer": "Formal",
                    "option_id": 10  # optional, if applicable
                },
                ...
            ]
        }
        """
        data = request.get_json()
        participant_id = data['participant_id']
        answers = data['answers']
        # enumerator_id = get_jwt_identity()

        for ans in answers:
            answer = QuestionAnswer(
                participant_id=participant_id,
                # enumerator_id=enumerator_id,
                question_id=ans['question_id'],
                answer=ans['answer'],
                created_at=datetime.utcnow()
            )
            db.session.add(answer)
            db.session.flush()  # get answer.id

            # If option_id is provided, link it
            if ans.get('option_id'):
                from ...db.models.model import AnswerOptionSelected
                option_selected = AnswerOptionSelected(
                    question_answer_id=answer.id,
                    option_id=ans['option_id']
                )
                db.session.add(option_selected)

        db.session.commit()
        return {'message': 'Answers submitted successfully'}, 201
