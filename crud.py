from sqlalchemy.orm import Session
import models

async def create_resume(db: Session, filename: str, file_type: str, content: str) -> models.Resume:
    resume = models.Resume(filename=filename, file_type=file_type, content=content)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume