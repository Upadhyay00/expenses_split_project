import jwt
from functools import wraps
from flask import request, jsonify,current_app
from models import User  # Import your User model


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Get token from request headers
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Expecting "Bearer <token>"

        if not token:
            return jsonify({'message': 'Unauthorized Request'}), 401

        try:
            secret_key = current_app.config['JWT_SECRET_KEY']
            # Decode and verify the token
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            # Fetch the user ID from the token and attach it to the request context
            user = User.query.filter_by(id=data['user_id']).first()
            if not user:
                return jsonify({'message': 'User not found!'}), 401

            request.user = user
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)

    return decorated