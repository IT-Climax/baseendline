from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, and_, cast, Date, Time
from datetime import datetime, time
from ...db.core import db
from ...db.models import Participant, User, RoleEnum


class EnumeratorDailyReportResource(Resource):
    @jwt_required()
    def get(self):
        """
        {
          "enumerator_id": 12,
          "date": "2025-05-12",
          "total_participants": 15,
          "first_recorded_at": "2025-05-12T08:15:23.456789",
          "last_recorded_at": "2025-05-12T16:45:10.123456",
          "cumulative_participants": 234
        }
        """

        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return {'message': 'User not found'}, 404

        # Parse date param or default to today
        date_str = request.args.get('date')
        if date_str:
            try:
                report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400
        else:
            report_date = datetime.utcnow().date()

        # Determine enumerator to report on
        enumerator_id = request.args.get('enumerator_id', type=int)
        if enumerator_id:
            # Only admins can query other enumerators
            if user.user_type not in [RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN]:
                return {'message': 'Access forbidden'}, 403
        else:
            enumerator_id = current_user_id

        # Working hours boundaries
        start_time = time(8, 0, 0)
        end_time = time(17, 0, 0)

        # Query participants recorded by enumerator on the date within working hours
        participants_query = db.session.query(Participant).filter(
            Participant.user_id == enumerator_id,
            cast(Participant.submitted_at, Date) == report_date,
            and_(
                cast(Participant.submitted_at, Time) >= start_time,
                cast(Participant.submitted_at, Time) <= end_time
            )
        )

        total_participants = participants_query.count()

        first_record = participants_query.order_by(Participant.submitted_at.asc()).first()
        last_record = participants_query.order_by(Participant.submitted_at.desc()).first()
        # Cumulative participants up to and including report_date (all times)
        cumulative_count = db.session.query(Participant).filter(
            Participant.user_id == enumerator_id,
            cast(Participant.submitted_at, Date) <= report_date
        ).count()

        return {
            'enumerator_id': enumerator_id,
            'date': report_date.isoformat(),
            'total_participants': total_participants,
            'first_recorded_at': first_record.submitted_at.isoformat() if first_record else None,
            'last_recorded_at': last_record.submitted_at.isoformat() if last_record else None,
            'cumulative_participants': cumulative_count
        }, 200
