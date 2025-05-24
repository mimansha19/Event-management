# Hashing and verifying user passwords
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password): # Secure password hash
    return generate_password_hash(password)

def verify_password(password, hash): # Verify password against hash
    return check_password_hash(hash, password)