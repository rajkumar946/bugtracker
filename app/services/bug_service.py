from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.bug import Bug
from app.schemas.bug import BugCreate
from app.models.user import User

async def create_bug(db: AsyncSession, bug_in: BugCreate, reporter_id: int):
    bug = Bug(
        title=bug_in.title,
        description=bug_in.description,
        project_id=bug_in.project_id,
        assigned_to_id=bug_in.assigned_to_id,
        reported_by_id=reporter_id,
        os=bug_in.os,
        browser=bug_in.browser,
        system_details=bug_in.system_details,
        device_info=bug_in.device_info,
        module=bug_in.module,
        expected_behavior=bug_in.expected_behavior,
        current_behavior=bug_in.current_behavior,
        steps_to_reproduce=bug_in.steps_to_reproduce,
        resolution=bug_in.resolution,
        replicated_on_mobile=bug_in.replicated_on_mobile,
        replicated_on_tablet=bug_in.replicated_on_tablet,
        replicated_on_desktop=bug_in.replicated_on_desktop,
        is_security_related=bug_in.is_security_related,
        is_regression=bug_in.is_regression,
        priority=bug_in.priority,
        severity=bug_in.severity,
    )
    db.add(bug)
    await db.commit()
    await db.refresh(bug)
    return bug


async def get_bug_by_id(db: AsyncSession, bug_id: int):
    result = await db.execute(select(Bug).where(Bug.id == bug_id))
    return result.scalar_one_or_none()

async def list_bugs(db: AsyncSession, project_id: int):
    result = await db.execute(select(Bug).where(Bug.project_id == project_id))
    return result.scalars().all()
