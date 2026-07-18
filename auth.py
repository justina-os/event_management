from passlib.context import CryptContext

pwd=CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_password(initial_password):
    return pwd.hash(initial_password)

def verify_password(initial_password,hashed_password):
    return pwd.verify(initial_password,hashed_password)