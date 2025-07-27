from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.models.user import User
from app.models.project_user import ProjectUser

async def create_project(project_in: ProjectCreate, user_id: int, db: AsyncSession):
    project = Project(**project_in.model_dump(), created_by_id=user_id)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project

async def get_project_by_id(project_id: int, db: AsyncSession):
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalars().first()

async def get_all_projects(db: AsyncSession, currentUser: User):
    result = await db.execute(select(Project))
    return result.scalars().all()

async def update_project(project_id: int, project_in: ProjectUpdate, db: AsyncSession):
    project = await get_project_by_id(project_id, db)
    if project:
        for key, value in project_in.model_dump(exclude_unset=True).items():
            setattr(project, key, value)
        await db.commit()
        await db.refresh(project)
    return project

async def delete_project(project_id: int, db: AsyncSession):
    project = await get_project_by_id(project_id, db)
    if project:
        await db.delete(project)
        await db.commit()
    return project

async def add_user_to_project(db: AsyncSession, project_id: int, user_id: int):
    # Check if user is already in the project
    result = await db.execute(
        select(ProjectUser).where(ProjectUser.project_id == project_id, ProjectUser.user_id == user_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already in project")

    association = ProjectUser(project_id=project_id, user_id=user_id)
    db.add(association)
    await db.commit()
    return {"message": "User added to project"}

async def remove_user_from_project(db: AsyncSession, project_id: int, user_id: int):
    result = await db.execute(
        select(ProjectUser).where(ProjectUser.project_id == project_id, ProjectUser.user_id == user_id)
    )
    association = result.scalar_one_or_none()
    if not association:
        raise HTTPException(status_code=404, detail="User not in project")

    await db.delete(association)
    await db.commit()
    return {"message": "User removed from project"}