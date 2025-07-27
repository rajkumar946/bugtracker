from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.admin import AdminCreateUser, AdminUpdateUser
from app.schemas.user import UserSelfUpdate
from app.services.admin_service import (
    create_user_as_admin,
    update_user_admin,
    delete_user_admin,
)
from app.services.user_service import update_user_self
from app.core.roles import UserRoles
from app.db.session import get_db
from app.models.user import User
from app.dependencies import require_roles, get_current_user

router = APIRouter()

@router.put("/me")
async def update_own_profile(
    data: UserSelfUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await update_user_self(current_user.id, data, db)

@router.post("", dependencies=[Depends(require_roles(UserRoles.ADMIN, UserRoles.MANAGER))])
async def create_user(data: AdminCreateUser, db: AsyncSession = Depends(get_db)):
    return await create_user_as_admin(data, db)

@router.put("/{user_id}", dependencies=[Depends(require_roles(UserRoles.ADMIN, UserRoles.MANAGER))])
async def update_user(user_id: int, data: AdminUpdateUser, db: AsyncSession = Depends(get_db)):
    return await update_user_admin(user_id, data, db)

@router.delete("/{user_id}", dependencies=[Depends(require_roles(UserRoles.ADMIN, UserRoles.MANAGER))])
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_user_admin(user_id, db)