import os
import json
import logging
from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...db.core import db
from ...db.models import ParticipantClass, FGDQuestion, FGDQuestionOption, FGDParticipant, FGDAnswer, User, RoleEnum
from ...utils.auth import role_required


def is_admin():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return user and user.user_type in [RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN]


class FGDQuestionsFileUploadResource(Resource):
    @jwt_required()
    @role_required('ADMIN', 'SUPER_ADMIN')
    def post(self):
        # Path to JSON file
        json_path = os.path.join(current_app.root_path, 'scripts', 'fgd_questions.json')
        if not os.path.exists(json_path):
            return {'message': 'Questions JSON file not found on server'}, 500

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'classes' not in data:
            return {'message': 'Invalid JSON format: missing "classes"'}, 400
        FGDQuestionOption.query.delete()
        FGDQuestion.query.delete()
        ParticipantClass.query.delete()
        db.session.commit()

        # Insert fresh data
        for cls_data in data['classes']:
            class_name = cls_data.get('name')
            if not class_name:
                return {'message': 'Each class must have a name'}, 400

            participant_class = ParticipantClass(name=class_name)
            db.session.add(participant_class)
            db.session.flush()

            questions = cls_data.get('questions', [])
            for q_data in questions:
                q_text = q_data.get('question_text')
                q_type = q_data.get('question_type')
                q_order = q_data.get('question_order')

                if not all([q_text, q_type, q_order]):
                    return {'message': f'Missing fields in question under class {class_name}'}, 400

                question = FGDQuestion(
                    participant_class_id=participant_class.id,
                    question_text=q_text,
                    question_type=q_type,
                    question_order=q_order
                )
                db.session.add(question)
                db.session.flush()

                if q_type == 'multiple_choice':
                    options = q_data.get('options', [])
                    for opt_data in options:
                        opt_text = opt_data.get('option_text')
                        opt_order = opt_data.get('option_order')
                        if not opt_text or opt_order is None:
                            return {'message': f'Invalid option in question "{q_text}"'}, 400

                        option = FGDQuestionOption(
                            question_id=question.id,
                            option_text=opt_text,
                            option_order=opt_order
                        )
                        db.session.add(option)
        db.session.commit()
        return {'message': 'FGD questions reloaded successfully from file'}, 201


class FGDQuestionUpdateResource(Resource):
    @jwt_required()
    @role_required('ADMIN', 'SUPER_ADMIN')
    def put(self, question_id):
        """
        Update a single question and its options by question_id.
        JSON payload example:
        {
          "question_text": "Updated question text",
          "question_type": "text",
          "question_order": 1,
          "options": [  # optional, only for multiple_choice
            {"option_text": "Option 1", "option_order": 1},
            {"option_text": "Option 2", "option_order": 2}
          ]
        }
        """
        question = FGDQuestion.query.get_or_404(question_id)
        data = request.get_json()

        question_text = data.get('question_text')
        question_type = data.get('question_type')
        question_order = data.get('question_order')

        if question_text:
            question.question_text = question_text
        if question_type:
            question.question_type = question_type
        if question_order is not None:
            question.question_order = question_order

        # Update options if question_type is multiple_choice
        if question.question_type == 'multiple_choice' and 'options' in data:
            FGDQuestionOption.query.filter_by(question_id=question.id).delete()
            db.session.flush()

            for opt_data in data['options']:
                opt_text = opt_data.get('option_text')
                opt_order = opt_data.get('option_order')
                if not opt_text or opt_order is None:
                    return {'message': 'Invalid option data'}, 400
                option = FGDQuestionOption(
                    question_id=question.id,
                    option_text=opt_text,
                    option_order=opt_order
                )
                db.session.add(option)

        db.session.commit()
        return {'message': f'Question {question_id} updated successfully'}, 200


class FGDQuestionsDeleteAllResource(Resource):
    @jwt_required()
    @role_required('ADMIN', 'SUPER_ADMIN')
    def delete(self):
        FGDQuestionOption.query.delete()
        FGDQuestion.query.delete()
        ParticipantClass.query.delete()
        db.session.commit()
        return {'message': 'All FGD questions and classes deleted'}, 200


class FGDQuestionsResource(Resource):
    @jwt_required()
    @role_required('ENUMERATOR', 'ADMIN', 'SUPER_ADMIN')
    def get(self, participant_class_id):
        participant_class = ParticipantClass.query.get(participant_class_id)
        if participant_class is None:
            return {"message": "Participant class not in the system"}, 404

        questions = FGDQuestion.query.filter_by(
            participant_class_id=participant_class.id
        ).order_by(FGDQuestion.question_order).all()

        result = []
        for q in questions:
            q_data = {
                'id': q.id,
                'question_text': q.question_text,
                'question_type': q.question_type,
                'question_order': q.question_order,
                'options': []
            }
            if q.question_type == 'multiple_choice':
                options = FGDQuestionOption.query.filter_by(question_id=q.id).order_by(FGDQuestionOption.option_order).all()
                q_data['options'] = [
                    {'id': opt.id, 'option_text': opt.option_text, 'option_order': opt.option_order}
                    for opt in options
                ]
            result.append(q_data)
        response = {
            'participant_class': participant_class.name,
            'questions': result
        }
        logging.debug(f"FGDQuestionsResource response: {response}")
        return response, 200


class FGDSubmitAnswersResource(Resource):
    @jwt_required()
    @role_required('ADMIN', 'SUPER_ADMIN')
    def post(self):
        data = request.get_json()
        if not data:
            return {'message': 'Missing JSON payload'}, 400

        participant_class_id = data.get('participant_class_id')
        participant_info = data.get('participant')
        answers = data.get('answers')

        if not participant_class_id or not participant_info or not answers:
            return {'message': 'participant_class_id, participant info, and answers are required'}, 400

        participant_class = ParticipantClass.query.get(participant_class_id)
        if not participant_class:
            return {'message': 'Invalid participant_class_id'}, 400

        participant = FGDParticipant(
            participant_class_id=participant_class_id,
            name=participant_info.get('name'),
            gender=participant_info.get('gender'),
            age=participant_info.get('age'),
            contact_info=participant_info.get('contact_info')
        )
        db.session.add(participant)
        db.session.flush()  # to get participant.id

        # # Current enumerator user id
        # enumerator_id = get_jwt_identity()

        # Save answers
        for ans in answers:
            question_id = ans.get('question_id')
            selected_option_id = ans.get('selected_option_id')
            answer_text = ans.get('answer_text')

            if not question_id:
                db.session.rollback()
                return {'message': 'Each answer must include question_id'}, 400

            # Validate question exists
            question = FGDQuestion.query.get(question_id)
            if not question:
                db.session.rollback()
                return {'message': f'Question ID {question_id} does not exist'}, 400

            # Validate option if provided
            if selected_option_id:
                option = FGDQuestionOption.query.filter_by(id=selected_option_id, question_id=question_id).first()
                if not option:
                    db.session.rollback()
                    return {'message': f'Option ID {selected_option_id} is invalid for question {question_id}'}, 400

            # For required questions, you could add validation here (optional)

            answer = FGDAnswer(
                participant_id=participant.id,
                question_id=question_id,
                selected_option_id=selected_option_id,
                answer_text=answer_text
            )
            db.session.add(answer)

        db.session.commit()
        return {'message': 'Participant answers submitted successfully', 'participant_id': participant.id}, 201
