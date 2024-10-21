import re

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."

    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit."

    if not re.search(r'[\W_]', password):  # This checks for non-alphanumeric characters (special characters)
        return False, "Password must contain at least one special character."

    return True, None