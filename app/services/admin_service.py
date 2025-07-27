from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.models.bug import Bug
from app.core.security import hash_password
from sqlalchemy import delete
from fastapi import HTTPException

async def create_user_as_admin(data, db: AsyncSession):
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
        is_verified=True,
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def update_user_admin(user_id: int, data, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(404, "User not found")

    if data.email:
        user.email = data.email
    if data.password:
        user.hashed_password = hash_password(data.password)
    if data.role:
        user.role = data.role
    await db.commit()
    return user

async def delete_user_admin(user_id: int, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(404, "User not found")

    bug_result = await db.execute(
        select(Bug).where(Bug.assigned_to_id == user_id, Bug.status != "closed")
    )
    pending_bugs = bug_result.scalars().all()
    if pending_bugs:
        raise HTTPException(
            400, f"User has {len(pending_bugs)} unresolved bugs. Cannot delete."
        )

    await db.delete(user)
    await db.commit()
    return {"message": "User deleted"}

async def update_email_config(data):
    # You can store this in a config file, env, or DB (recommended)
    import os
    os.environ["SMTP_HOST"] = data.smtp_host
    os.environ["SMTP_PORT"] = str(data.smtp_port)
    os.environ["SMTP_USER"] = data.smtp_user
    os.environ["SMTP_PASS"] = data.smtp_pass
    os.environ["EMAIL_FROM"] = data.from_email
    return {"message": "Email configuration updated"}
