from sqlalchemy.orm import Session
from sqlalchemy.future import select
import models

async def create_resume(db: Session, uuid: str, original_filename: str, content: str) -> models.Resume:
    resume = models.Resume(uuid=uuid, original_filename=original_filename, content=content)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume

async def get_resume(db: Session, uuid:str) -> models.Resume | None:
    res = await db.execute(
        select(models.Resume).where(models.Resume.uuid == uuid)
    )
    return res.scalars().first()