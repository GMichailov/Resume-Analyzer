from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Response
from sqlalchemy.orm import Session
import shutil
from pathlib import Path
from . import database, models, crud, resume_parser
from uuid import uuid4

models.Base.metadata.create_all(bind=database.engine)

app=FastAPI()
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
FILES_DIR = Path("uploads/files")
FILES_DIR.mkdir(exist_ok=True)

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    filename = file.filename
    ext = Path(filename).suffix.lower()
    if ext not in (".pdf", ".docx"):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed.")
    fname = str(uuid4())+ext
    temp_path = FILES_DIR / fname
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        content = resume_parser.read_resume_file(temp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {e}")

    resume = crud.create_resume(db, filename=fname, content=content)

    return Response()
