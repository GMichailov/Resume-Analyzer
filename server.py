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
    index,
    load_index,
    add_to_index,
    query_index
)
from models import (
    Resume
)
from resume_parser import (
    read_resume
)
from schema import (
    BestResumeParms
)
from utils import (
    embedding_model,
)



from uuid import uuid4

Base.metadata.create_all(bind=engine)

UPLOAD_DIR = Path("uploads")
FILES_DIR = Path("uploads/files")
app=FastAPI()

@app.on_event("startup")
def start_up():
    global embedding_model
    global index
    UPLOAD_DIR.mkdir(exist_ok=True)
    FILES_DIR.mkdir(exist_ok=True)
    if not Path(UPLOAD_DIR / "index.ann").exists():
        create_index()
    load_index()
    

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload")
async def upload_resume(files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    for file in files:
        if Path(file).suffix.lower() not in (".pdf", ".docx"):
            raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed.")

    for file in files:
        original_filename = file.filename
        ext = Path(original_filename).suffix.lower()

        f_uuid = str(uuid4())
        temp_path = FILES_DIR / f_uuid+ext
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        try:
            content = read_resume(temp_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read file: {e}")

        add_task = asyncio.create_task(add_to_index(embedding_model, f_uuid, content))
        await create_resume(db, uuid=f_uuid, original_filename=original_filename, content=content)
        await add_task
        return Response(status_code=200)


@app.get("/improvements/")
async def get_resume_recommendations(job_description: bool=Query(...)):
    pass


@app.get("/best")
async def get_best_resumes_for_job_description(params: BestResumeParms):
    if params.job_description is None or len(params.job_description)==0:
        raise HTTPException(status_code=400, detail="Must have a job description.")
    
    if params.count > 5:
        params.count = 5
    elif params.count <= 0:
        params.count = 1

    best = query_index(
        job_description=params.job_description, 
        top_k=params.count,
    )






    