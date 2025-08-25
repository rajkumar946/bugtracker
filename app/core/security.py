from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, HashingError, VerificationError
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Initialize Argon2 password hasher with recommended settings
ph = PasswordHasher(
    time_cost=2,        # Number of iterations
    memory_cost=102400, # Memory usage in KiB (100MB)
    parallelism=8,      # Number of parallel threads
    hash_len=32,        # Length of the hash in bytes
    salt_len=16         # Length of the salt in bytes
)

def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a password against its hash using Argon2.
    
    Args:
        plain: Plain text password
        hashed: Argon2 hashed password
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        ph.verify(hashed, plain)
        return True
    except (VerifyMismatchError, VerificationError):
        return False
    except Exception:
        # Handle any other unexpected errors
        return False

def hash_password(password: str) -> str:
    """
    Hash a password using Argon2.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        str: Argon2 hashed password
        
    Raises:
        HashingError: If hashing fails
    """
    try:
        return ph.hash(password)
    except HashingError as e:
        raise Exception(f"Password hashing failed: {str(e)}")

def needs_rehash(hashed: str) -> bool:
    """
    Check if a password hash needs to be rehashed due to parameter changes.
    
    Args:
        hashed: Argon2 hashed password
        
    Returns:
        bool: True if hash needs updating, False otherwise
    """
    try:
        return ph.check_needs_rehash(hashed)
    except Exception:
        return True  # Assume rehash is needed if we can't check

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    """
    Decode a JWT token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        dict: Decoded token payload
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])