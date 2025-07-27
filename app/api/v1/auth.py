from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from app.db.session import get_db
from app.schemas import user as schemas
from app.services.user_service import (
    authenticate_user, initiate_password_reset,
    reset_password, verify_email
)
from app.core.security import create_access_token

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(form.username, form.password, db)
    if not user or not user.is_verified:
        raise HTTPException(status_code=400, detail="Invalid credentials or email not verified")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token}

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
