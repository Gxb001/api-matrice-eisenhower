from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from app.models.user import User


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        print(f"JWT Identity: {user_id}")
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        print(f"JWT Claims: {claims}")
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)

    return decorated_function


def user_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or (user.role != 'admin' and user_id != kwargs.get('user_id')):
            return jsonify({'error': 'Unauthorized'}), 403
        return f(*args, **kwargs)

    return decorated_function
