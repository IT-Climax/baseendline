from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def invalid_api_usage(message, status_code=400):
    payload = {
        'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error'),
        'message': message
    }
    response = jsonify(payload)
    response.status_code = status_code
    return response
