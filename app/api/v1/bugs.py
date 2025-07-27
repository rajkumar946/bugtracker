from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.bug import BugCreate, BugOut
from app.services.bug_service import create_bug, get_bug_by_id, list_bugs
from app.db.session import get_db
from app.core.roles import UserRoles
from app.dependencies import require_roles, get_current_user
from app.models.user import User

router = APIRouter()

# List all bugs from project
@router.get("/{project_id}",
    response_model=list[BugOut],
    dependencies=[
        Depends(
            require_roles(UserRoles.ADMIN, UserRoles.MANAGER, UserRoles.QA, UserRoles.USER, UserRoles.DEVELOPER)
        )
    ]
)
async def list_bugs_route(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await list_bugs(db, project_id)

# Get project bug details
@router.get("/{project_id}/bugs/{bug_id}",
    response_model=BugOut,
    dependencies=[
        Depends(
            require_roles(UserRoles.ADMIN, UserRoles.MANAGER, UserRoles.QA, UserRoles.USER, UserRoles.DEVELOPER)
        )
    ]
)
async def get_bug_route(
    bug_id: int,
    db: AsyncSession = Depends(get_db)
):
    bug = await get_bug_by_id(db, bug_id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return bug

# Create Bug in project
@router.post("/{project_id}/bugs",
    response_model=BugOut,
    dependencies=[
        Depends(
            require_roles(UserRoles.ADMIN, UserRoles.MANAGER, UserRoles.QA, UserRoles.USER)
        )
    ]
)
async def create_bug_route(
    bug_in: BugCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await create_bug(db, bug_in, reporter_id=current_user.id)
