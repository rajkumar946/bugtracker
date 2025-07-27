from fastapi import APIRouter, Depends

from app.schemas.admin import EmailSettings
from app.services.admin_service import update_email_config
from app.core.roles import UserRoles
from app.dependencies import require_roles

router = APIRouter()

@router.post("/admin/email-config",
    dependencies=[
        Depends(
            require_roles(UserRoles.ADMIN)
        )
    ]
)
async def update_email(data: EmailSettings):
    return await update_email_config(data)
