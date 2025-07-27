import secrets
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate, UserSelfUpdate
from app.core.security import hash_password, verify_password, create_access_token
from app.core.email import send_email

async def create_user(user_in: UserCreate, db: AsyncSession):
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
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def initiate_password_reset(email: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        await db.commit()
        await send_email(user.email, "Reset Password", f"/reset-password?token={token}")

async def reset_password(token: str, new_password: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.reset_token == token))
    user = result.scalars().first()
    if user:
        user.hashed_password = hash_password(new_password)
        user.reset_token = None
        await db.commit()
        return True
    return False

async def verify_email(token: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.verification_token == token))
    user = result.scalars().first()
    if user:
        user.is_verified = True
        user.verification_token = None
        await db.commit()
        return True
    return False

async def update_user_self(user_id: int, data: UserSelfUpdate, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.full_name is not None:
        user.full_name = data.full_name
    if data.email is not None:
        user.email = data.email
    if data.password is not None:
        user.hashed_password = hash_password(data.password)

    await db.commit()
    await db.refresh(user)
    return user
