from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ...db.models import Participant
from ...db.async_core import get_async_session
from ...utils.auth import role_required
from ...db.models import QuestionPhase, Section, QuestionBase, QuestionOptions, QuestionAnswer, AnswerOptionSelected
from sqlalchemy.future import select


class ParticipantRegistrationResource(Resource):
    method_decorators = [jwt_required(), role_required('ENUMERATOR', 'ADMIN', 'SUPER_ADMIN')]

    async def post(self):
        data = await request.get_json()
        user_id = get_jwt_identity()

        participant = Participant(
            user_id=user_id,
            age=data['age'],
            marital_status=data['marital_status'],
            location=data['location'],
            education=data['education'],
            highest_formal_education=data['highest_formal_education'],
            coordinates=data.get('coordinates'),
            nin=data.get('nin'),
            status=data.get('status'),
            submitted_at=datetime.utcnow().isoformat()
        )

        async_session = await get_async_session()
        async with async_session as session:
            session.add(participant)
            await session.commit()
            await session.refresh(participant)

        return {'message': 'Participant registered', 'participant_id': participant.id}, 201


class ParticipantQuestionsResource(Resource):
    method_decorators = [jwt_required(), role_required('ENUMERATOR', 'ADMIN', 'SUPER_ADMIN')]

    async def get(self):
        phase_name = request.args.get('phase', 'Baseline')
        async_session = await get_async_session()
        async with async_session as session:
            phase = (await session.execute(select(QuestionPhase).filter_by(title=phase_name))).scalar_one_or_none()
            if not phase:
                return {'message': f'Phase {phase_name} not found'}, 404

            sections = (await session.execute(select(Section))).scalars().all()
            result = []
            for section in sections:
                root_questions = (await session.execute(
                    select(QuestionBase)
                    .filter_by(section_id=section.id, phase_id=phase.id, parent_question_id=None)
                    .order_by(QuestionBase.display_order)
                )).scalars().all()
                if not root_questions:
                    continue

                section_data = {
                    'section_id': section.id,
                    'section_title': section.title,
                    'questions': []
                }
                for root_q in root_questions:
                    q_data = await self._process_question_with_children(session, root_q)
                    section_data['questions'].append(q_data)
                result.append(section_data)

        return {'phase': phase_name, 'sections': result}, 200

    async def _process_question_with_children(self, session, question):
        options = []
        question_options = (await session.execute(
            select(QuestionOptions).filter_by(question_id=question.id)
        )).scalars().all()
        for opt in question_options:
            opt_data = {
                'id': opt.id,
                'title': opt.title,
                'follow_up_question_id': opt.follow_up_question_id,
                'follow_up': None
            }
            if opt.follow_up_question_id:
                follow_up_q = (await session.execute(
                    select(QuestionBase).filter_by(id=opt.follow_up_question_id)
                )).scalar_one_or_none()
                if follow_up_q:
                    opt_data['follow_up'] = await self._process_question_with_children(session, follow_up_q)
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
    method_decorators = [jwt_required(), role_required('ENUMERATOR', 'ADMIN', 'SUPER_ADMIN')]

    async def post(self):
        data = await request.get_json()
        participant_id = data['participant_id']
        answers = data['answers']
        enumerator_id = get_jwt_identity()

        async_session = await get_async_session()
        async with async_session as session:
            for ans in answers:
                answer = QuestionAnswer(
                    participant_id=participant_id,
                    enumerator_id=enumerator_id,
                    question_id=ans['question_id'],
                    answer=ans['answer'],
                    created_at=datetime.utcnow()
                )
                session.add(answer)
                await session.flush()  # get answer.id

                # If option_id is provided, link it
                if ans.get('option_id'):
                    option_selected = AnswerOptionSelected(
                        question_answer_id=answer.id,
                        option_id=ans['option_id']
                    )
                    session.add(option_selected)

            await session.commit()

        return {'message': 'Answers submitted successfully'}, 201
