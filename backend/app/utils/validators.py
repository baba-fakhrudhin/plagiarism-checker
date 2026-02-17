import re

def allowed_file(filename):
    """Check if file extension is allowed"""
    allowed_extensions = {'txt', 'pdf', 'docx', 'pptx', 'doc', 'ppt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True