from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.storage.attachment_storage import save_attachment
from app.models.attachment import Attachment

async def save_bug_attachment(db: AsyncSession, bug_id: int, file: UploadFile):
    file_path_or_url = await save_attachment(file, "bugs", bug_id)
    attachment = Attachment(file_path=file_path_or_url, bug_id=bug_id)
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)
    return attachment
