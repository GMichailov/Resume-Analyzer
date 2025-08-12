from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Response, Query
from sqlalchemy.orm import Session
import shutil
from pathlib import Path
import asyncio
from crud import (
    create_resume
)
from database import (
    create_index,
    Base,
    engine,
    SessionLocal,
    add_to_index
)
from models import (
    Resume
)
from resume_parser import (
    read_resume
)
from utils import (
    load_embedding_model
)



from uuid import uuid4

Base.metadata.create_all(bind=engine)

UPLOAD_DIR = Path("uploads")
FILES_DIR = Path("uploads/files")
embedding_model = None
app=FastAPI()

@app.on_event("startup")
def start_up():
    global embedding_model
    UPLOAD_DIR.mkdir(exist_ok=True)
    FILES_DIR.mkdir(exist_ok=True)
    embedding_model = load_embedding_model()
    if not Path(UPLOAD_DIR / "index.ann").exists():
        create_index()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    filename = file.filename
    ext = Path(filename).suffix.lower()
    if ext not in (".pdf", ".docx"):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed.")
    fname = str(uuid4())
    temp_path = FILES_DIR / fname+ext
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        content = read_resume(temp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {e}")

    add_task = asyncio.create_task(add_to_index(embedding_model, fname, content))
    await create_resume(db, filename=fname, content=content)
    await add_task
    return Response(status_code=200)


@app.get("/improvements/")
async def get_resume_recommendations(job_description=Query(...)):
    pass


@app.get("/best")
async def get_best_resume_for_job_description():
    pass