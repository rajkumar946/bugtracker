# app/services/user_service.py
import secrets
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate, UserSelfUpdate
from app.core.security import hash_password, verify_password, create_access_token, needs_rehash
from app.core.email import send_email

async def create_user(user_in: UserCreate, db: AsyncSession):
    """
    Create a new user with email verification.
    
    Args:
        user_in: User creation data
        db: Database session
        
    Returns:
        User: Created user instance
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    token = secrets.token_urlsafe(32)
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        verification_token=token,
        is_verified=False
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    await send_email(
        user.email,
        "Verify your email",
        f"Please verify your email: /verify-email?token={token}"
    )
    return user

async def authenticate_user(email: str, password: str, db: AsyncSession):
    """
    Authenticate user and optionally rehash password if needed.
    
    Args:
        email: User's email
        password: Plain text password
        db: Database session
        
    Returns:
        User or None: User instance if authentication successful, None otherwise
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    # Check if password hash needs updating (Argon2 parameter upgrade)
    if needs_rehash(user.hashed_password):
        try:
            user.hashed_password = hash_password(password)
            await db.commit()
        except Exception:
            # Log error but don't fail authentication
            pass
    
    return user

async def initiate_password_reset(email: str, db: AsyncSession):
    """
    Initiate password reset process.
    
    Args:
        email: User's email
        db: Database session
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        await db.commit()
        await send_email(user.email, "Reset Password", f"/reset-password?token={token}")

async def reset_password(token: str, new_password: str, db: AsyncSession):
    """
    Reset user password using reset token.
    
    Args:
        token: Password reset token
        new_password: New plain text password
        db: Database session
        
    Returns:
        bool: True if reset successful, False otherwise
    """
    result = await db.execute(select(User).where(User.reset_token == token))
    user = result.scalars().first()
    if user:
        user.hashed_password = hash_password(new_password)
        user.reset_token = None
        await db.commit()
        return True
    return False

async def verify_email(token: str, db: AsyncSession):
    """
    Verify user email using verification token.
    
    Args:
        token: Email verification token
        db: Database session
        
    Returns:
        bool: True if verification successful, False otherwise
    """
    result = await db.execute(select(User).where(User.verification_token == token))
    user = result.scalars().first()
    if user:
        user.is_verified = True
        user.verification_token = None
        await db.commit()
        return True
    return False

async def update_user_self(user_id: int, data: UserSelfUpdate, db: AsyncSession):
    """
    Update user's own profile information.
    
    Args:
        user_id: User's ID
        data: Update data
        db: Database session
        
    Returns:
        User: Updated user instance
        
    Raises:
        HTTPException: If user not found
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.full_name is not None:
        user.full_name = data.full_name
    if data.email is not None:
        # Check if new email is already taken
        if data.email != user.email:
            email_check = await db.execute(select(User).where(User.email == data.email))
            existing_user = email_check.scalars().first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already in use")
        user.email = data.email
    if data.password is not None:
        user.hashed_password = hash_password(data.password)

    await db.commit()
    await db.refresh(user)
    return user