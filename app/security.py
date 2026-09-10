from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from .config import JWT_SECRET

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(value): return pwd.hash(value)
def verify_password(value, hashed): return pwd.verify(value, hashed)
def create_token(user_id, role):
    return jwt.encode({"sub": str(user_id), "role": role, "exp": datetime.now(timezone.utc)+timedelta(hours=24)}, JWT_SECRET, algorithm="HS256")
