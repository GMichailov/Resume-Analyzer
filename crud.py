from sqlalchemy.orm import Session
import models

async def create_resume(db: Session, uuid: str, original_filename: str, content: str) -> models.Resume:
    resume = models.Resume(uuid=uuid, original_filename=original_filename, content=content)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume