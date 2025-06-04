"""
Script to upload Education section questions into the database.
"""

from ..db.core import db
from ..db.models.model import Section, QuestionBase, QuestionOptions, QuestionPhase


def upload_education_questions():
    # 1. Ensure the "Education" section exists
    section = Section.query.filter_by(title='Education').first()
    if not section:
        section = Section(title='Education')
        db.session.add(section)
        db.session.commit()
    print(f"Section ID for Education: {section.id}")

    # 2. Ensure the "Baseline" phase exists
    phase = QuestionPhase.query.filter_by(title='Baseline').first()
    if not phase:
        phase = QuestionPhase(title='Baseline')
        db.session.add(phase)
        db.session.commit()
    print(f"Phase ID for Baseline: {phase.id}")

    questions_data = [
        {
            "question_id": 1,
            "question_no": "1",
            "question_title": "Are you currently enrolled any of these educational programs?",
            "parent_question_id": None,
            "answer_options": [
                {"title": "Formal", "follow_up": 2},
                {"title": "Vocational", "follow_up": 2},
                {"title": "Both", "follow_up": 2},
                {"title": "None", "follow_up": 3}
            ],
            "tags": "education, baseline"
        },
        {
            "question_id": 2,
            "question_no": "1a",
            "question_title": "How many hours do you spend on the program?",
            "parent_question_id": 1,
            "answer_options": [
                {"title": "Less than 5", "follow_up": None},
                {"title": "5-10", "follow_up": None},
                {"title": "10-15", "follow_up": None},
                {"title": "More than 15", "follow_up": None}
            ],
            "tags": "education, time_commitment, participation, baseline"
        },
        {
            "question_id": 3,
            "question_no": "1b",
            "question_title": "would you like to be enrolled on any of this?",
            "parent_question_id": 1,
            "answer_options": [
                {"title": "Yes", "follow_up": 4},
                {"title": "No", "follow_up": None}
            ],
            "tags": "education, enrollment_interest, access, aspiration, baseline"
        },
        {
            "question_id": 4,
            "question_no": "1c",
            "question_title": "Which of them would you like to be enrolled in?",
            "parent_question_id": 3,
            "answer_options": [
                {"title": "Formal", "follow_up": None},
                {"title": "Vocational", "follow_up": None}
            ],
            "tags": "education, enrollment_preference, access, baseline"
        },
        {
            "question_id": 5,
            "question_no": "2",
            "question_title": "Have you received any assistive devices to help with your education?",
            "parent_question_id": None,
            "answer_options": [
                {"title": "Yes", "follow_up": None},
                {"title": "No", "follow_up": None}
            ],
            "tags": "education, assistive_technology, accessibility, baseline"
        },
        {
            "question_id": 6,
            "question_no": "3",
            "question_title": "How often do you attend training or sessions?",
            "parent_question_id": 2,
            "answer_options": [
                {"title": "Daily", "follow_up": 7},
                {"title": "Weekly", "follow_up": 7},
                {"title": "Monthly", "follow_up": 7}
            ],
            "tags": "education, attendance, participation, frequency, baseline"
        },
        {
            "question_id": 7,
            "question_no": "4",
            "question_title": "How has the availability of assistive technologies (if any) impacted your ability to pursue education?",
            "parent_question_id": 6,
            "answer_options": [
                {"title": "Not impacted", "follow_up": 8},
                {"title": "Barely impacted", "follow_up": 8},
                {"title": "Moderately impacted", "follow_up": 8},
                {"title": "Greatly impacted", "follow_up": 8}
            ],
            "tags": "education, assistive_technology, impact, accessibility, baseline"
        },
        {
            "question_id": 8,
            "question_no": "5",
            "question_title": "What challenges do you face in accessing education, especially as a person with a disability?",
            "parent_question_id": 7,
            "answer_options": [
                {"title": "Input box", "follow_up": 9}
            ],
            "tags": "education, barriers, disability, access, challenges, baseline"
        },
        {
            "question_id": 9,
            "question_no": "6",
            "question_title": "What kind of support do you think would improve your access to education?",
            "parent_question_id": 8,
            "answer_options": [
                {"title": "Input box", "follow_up": None}
            ],
            "tags": "education, support_needs, access, recommendations, baseline"
        },
    ]

    # 4. Insert questions first (so all question IDs exist)
    question_objs = {}
    for q in questions_data:
        exists = QuestionBase.query.filter_by(id=q["question_id"]).first()
        if exists:
            print(f"Question {q['question_id']} already exists, skipping.")
            question_objs[q["question_id"]] = exists
            continue
        question = QuestionBase(
            id=q["question_id"],
            title=q["question_title"],
            type="multiple" if len(q["answer_options"]) > 1 and "Input box" not in [o['title'] for o in q["answer_options"]] else "text",
            section_id=section.id,
            parent_question_id=q["parent_question_id"],
            phase_id=phase.id,
            is_required=False,
            display_order=int(q["question_id"]),
            tags=q["tags"],
            help_text=None
        )
        db.session.add(question)
        db.session.flush()
        question_objs[q["question_id"]] = question

    db.session.commit()

    # 5. Insert options with follow-up logic
    for q in questions_data:
        question = question_objs[q["question_id"]]
        for opt in q["answer_options"]:
            exists_opt = QuestionOptions.query.filter_by(title=opt["title"], question_id=question.id).first()
            if exists_opt:
                continue
            option = QuestionOptions(
                title=opt["title"],
                question_id=question.id,
                follow_up_question_id=opt["follow_up"]
            )
            print("about to commit options")
            db.session.add(option)
    db.session.commit()
    print("Education questions and options with follow-up logic uploaded successfully.")
