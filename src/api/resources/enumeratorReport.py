from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, time, timedelta
from sqlalchemy import cast, Date
from ...db.core import db
from ...db.models import Participant, User, RoleEnum


class EnumeratorDailyReportResource(Resource):
    @jwt_required()
    def get(self):
        """
        Get daily report for enumerator:
        - total participants recorded on the date within working hours (8am-5pm)
        - first record timestamp during working hours
        - last record timestamp during working hours
        - cumulative total participants recorded up to and including the date

        Query params:
          date=YYYY-MM-DD (optional, defaults to today)
          enumerator_id (optional, admins only)
        """
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return {'message': 'User not found'}, 404

        # Parse date parameter or default to today
        date_str = request.args.get('date')
        if date_str:
            try:
                report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400
        else:
            report_date = datetime.utcnow().date()

        # Determine which enumerator to report on
        enumerator_id = request.args.get('enumerator_id', type=int)
        if enumerator_id:
            # Only admins and super admins can query other enumerators
            if user.user_type not in [RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN]:
                return {'message': 'Access forbidden'}, 403
        else:
            enumerator_id = current_user_id

        # Define working hours datetime range for the report date
        start_datetime = datetime.combine(report_date, time(8, 0, 0))
        end_datetime = datetime.combine(report_date, time(17, 0, 0))

        # Query participants recorded by enumerator on the date within working hours
        daily_query = db.session.query(Participant).filter(
            Participant.user_id == enumerator_id,
            Participant.submitted_at >= start_datetime,
            Participant.submitted_at <= end_datetime
        )

        total_participants = daily_query.count()

        first_record = daily_query.order_by(Participant.submitted_at.asc()).first()
        last_record = daily_query.order_by(Participant.submitted_at.desc()).first()

        # Cumulative participants up to and including the report date (all times)
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
