from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_db
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services import project_service
from app.dependencies import get_current_user, require_roles
from app.models.user import User
from app.core.roles import UserRoles
from app.schemas.project import ProjectUserAction

router = APIRouter()

# List out all projects
@router.get("/",
    response_model=List[ProjectResponse],
    dependencies=[
        Depends(
            require_roles(UserRoles.ADMIN, UserRoles.DEVELOPER, UserRoles.MANAGER, UserRoles.QA, UserRoles.USER)
        )
    ]
)
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await project_service.get_all_projects(db, current_user)

# Create project
@router.post("/",
    response_model=ProjectResponse,
    dependencies=[
        Depends(
            require_roles(UserRoles.ADMIN, UserRoles.MANAGER)
        )
    ]
)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await project_service.create_project(project_in, current_user.id, db)

# Get Project Details
@router.get("/{project_id}",
    response_model=ProjectResponse,
    dependencies=[]
)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project_by_id(project_id, db)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# Update project details
@router.put("/{project_id}",
    response_model=ProjectResponse,
    dependencies=[
        Depends(
            require_roles(UserRoles.MANAGER, UserRoles.ADMIN)
        )
    ]
)
async def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project_by_id(project_id, db)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await project_service.update_project(project_id, project_in, db)


# Delete project
@router.delete("/{project_id}",
    dependencies=[
        Depends(
            require_roles(UserRoles.ADMIN, UserRoles.MANAGER)
        )
    ]
)
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    project = await project_service.delete_project(project_id, db)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"detail": "Project deleted"}

# Add users to project
@router.post("/{project_id}/users",
    dependencies=[
        Depends(
            require_roles(UserRoles.ADMIN, UserRoles.MANAGER)
        )
    ]
)
async def add_user(project_id: int, data: ProjectUserAction, db: AsyncSession = Depends(get_db)):
    return await project_service.add_user_to_project(db, project_id=project_id, user_id=data.user_id)

# Remove user from project
@router.delete("/{project_id}/users",
    dependencies=[
        Depends(
            require_roles(UserRoles.ADMIN, UserRoles.MANAGER)
        )
    ]
)
async def remove_user(project_id: int, data: ProjectUserAction, db: AsyncSession = Depends(get_db)):
    return await project_service.remove_user_from_project(db, project_id=project_id, user_id=data.user_id)