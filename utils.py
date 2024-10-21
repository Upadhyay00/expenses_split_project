from datetime import datetime, timedelta
import jwt
from flask import current_app

def validate_percentage_split(participants):
    total_percentage = sum(p['percentage'] for p in participants)
    if total_percentage != 100:
        raise ValueError("Total percentage must equal 100%")
    return True

def calculate_split(total_amount, participants, method):
    if method == 'equal':
        split_amount = total_amount / len(participants)
        for p in participants:
            p['amount_owed'] = split_amount
    elif method == 'exact':
        for p in participants:
            if 'amount_owed' not in p:
                raise ValueError("Exact amounts must be provided for each participant")
    elif method == 'percentage':
        validate_percentage_split(participants)
        for p in participants:
            p['amount_owed'] = total_amount * (p['percentage'] / 100)
    return participants

def generate_jwt(user_id, expiration_minutes=30):
    # Get the JWT_SECRET_KEY from the app's configuration
    secret_key = current_app.config['JWT_SECRET_KEY']
    
    expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)
    token = jwt.encode({'user_id': user_id, 'exp': expiration}, secret_key, algorithm='HS256')
    return token
