from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import user as schemas
from app.services.user_service import (
    authenticate_user, initiate_password_reset,
    reset_password, verify_email
)
from app.core.security import create_access_token
from app.core.config import Settings

router = APIRouter()
settings = Settings()

@router.post("/login", response_model=schemas.Token)
async def login(form: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(form.email, form.password, db)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_verified:
        raise HTTPException(status_code=400, detail="Email is not verified")
    
    # generate access + refresh tokens
    access_expires = timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expires = timedelta(settings.REFRESH_TOKEN_EXPIRE_DAYS)
                                
    access_token = create_access_token(
        {"sub": str(user.id)},
        expires_delta=access_expires
    )

    refresh_token = create_access_token(
        {"sub": str(user.id)},
        expires_delta=refresh_expires
    )

    return {
        "user": schemas.UserInDB.from_orm(user),
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "expiresIn": int(access_expires.total_seconds()),
    }

@router.post("/forgot-password")
async def forgot_password(data: schemas.ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    await initiate_password_reset(data.email, db)
    return {"message": "Reset link sent if email exists."}

@router.post("/reset-password")
async def reset(data: schemas.ResetPassword, db: AsyncSession = Depends(get_db)):
    if await reset_password(data.token, data.new_password, db):
        return {"message": "Password reset successful"}
    raise HTTPException(status_code=400, detail="Invalid token")

@router.post("/verify-email")
async def verify(data: schemas.EmailVerificationRequest, db: AsyncSession = Depends(get_db)):
    if await verify_email(data.token, db):
        return {"message": "Email verified successfully"}
    raise HTTPException(status_code=400, detail="Invalid or expired token")
