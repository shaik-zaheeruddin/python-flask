from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from models import User

def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print('in role required')
            current_user = get_jwt_identity()
            print('current_user',current_user)
            user = User.query.filter_by(id=current_user).first()
            if user.role != role:
                return jsonify({"message": "Access forbidden: You do not have the required role"}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator