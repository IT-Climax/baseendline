from functools import wraps
from flask_jwt_extended import get_jwt_identity, jwt_required
from ..db.models.model import User
from flask import jsonify


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if user is None or user.user_type.name not in roles:
                return {"msg": "Access forbidden: insufficient permissions"}, 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


