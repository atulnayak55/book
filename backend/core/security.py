# core/security.py
from passlib.context import CryptContext

# Tell passlib to use the bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Checks if a plain password matches the hashed one in the database."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Scrambles the password before saving it to the database."""
    return pwd_context.hash(password)