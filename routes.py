from flask import Blueprint, request, jsonify, Response, make_response
from models import db, User, Expense, Participant
from utils import calculate_split, generate_jwt
from validators import validate_password
from werkzeug.security import generate_password_hash, check_password_hash
import csv
from io import StringIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from flask import send_file
from decorators import token_required

bp = Blueprint('api', __name__)

# User Registration
@bp.route('/register_user', methods=['POST'])
def create_user():
    data = request.get_json()

    # Validate the password
    password = data['password']
    is_valid, error_message = validate_password(password)

    if not is_valid:
        return jsonify({"error": error_message}), 400  # Return validation error if the password doesn't meet criteria
    
    # Check if the email already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "Email already exists! use other email to register"}), 400 

    # Hash the password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

    # Create a new user with the hashed password
    user = User(
        name=data['name'],
        email=data['email'],
        mobile_number=data['mobile_number'],
        password=hashed_password  # Store the hashed password
    )

    # Add the new user to the database
    db.session.add(user)
    db.session.commit()

    # Return a success message with the user ID
    return jsonify({"message": "User created", "user_id": user.id}), 201


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Get the user from the database
    user = User.query.filter_by(email=data.get('email')).first()

    # Verify user exists and password matches
    if not user or not check_password_hash(user.password, data.get('password')):
        return make_response(jsonify({'message': 'Invalid email or password!'}), 401)

    # Generate JWT token for the user
    token = generate_jwt(user.id)
    return jsonify({'token': token})

# Fetch user details
@bp.route('/get_details/<int:mobile_number>', methods=['GET'])
def get_user(mobile_number):
    # Convert the mobile_number to a string if necessary
    mobile_number = str(mobile_number)

    # Query the user by mobile_number
    user = User.query.filter_by(mobile_number=mobile_number).first()

    # If the user is not found, return a 404 error
    if user is None:
        return jsonify({"error": "User not found"}), 404

    # Return user details if found
    return jsonify({"name": user.name, "mobile": user.mobile_number, "user_id": user.id})


# Add Expense
@bp.route('/expenses', methods=['POST'])
@token_required
def add_expense():
    data = request.get_json()
    creator_id = data['creator_id']
    split_method = data['split_method']
    total_amount = data['amount']
    participants = data['participants']  # List of participants
    
    # Validate split and calculate amounts
    try:
        split_result = calculate_split(total_amount, participants, split_method)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Create the expense
    expense = Expense(amount=total_amount, description=data.get('description'), creator_id=creator_id, split_method=split_method)
    db.session.add(expense)
    db.session.commit()

    # Add participants
    for p in split_result:
        participant = Participant(expense_id=expense.id, user_id=p['user_id'], amount_owed=p['amount_owed'], percentage=p.get('percentage'))
        db.session.add(participant)

    db.session.commit()
    return jsonify({"message": "Expense added"}), 201

# Get user-specific expenses
# @token_required
@bp.route('/expenses/<int:user_id>', methods=['GET'])
def get_user_expenses(user_id):
    expenses = Participant.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "expense_id": exp.expense_id,
        "amount_owed": exp.amount_owed
    } for exp in expenses])

# Download CSV balance sheet

@bp.route('/expenses/<int:user_id>/balance-sheet', methods=['GET'])
@token_required
def download_balance_sheet_csv(user_id):
    # Fetch user's expenses
    expenses = Participant.query.filter_by(user_id=user_id).all()
    
    # Create CSV in-memory buffer
    output = StringIO()
    writer = csv.writer(output)
    
    # Write CSV headers
    writer.writerow(['Expense ID', 'Description', 'Amount Owed', 'Total Amount', 'Split Method'])

    # Write expense details to CSV
    for exp in expenses:
        expense_data = Expense.query.get(exp.expense_id)
        writer.writerow([
            expense_data.id,
            expense_data.description,
            exp.amount_owed,
            expense_data.amount,
            expense_data.split_method
        ])

    # Prepare CSV response
    output.seek(0)
    response = Response(output, mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=user_{user_id}_balance_sheet.csv'
    
    return response
