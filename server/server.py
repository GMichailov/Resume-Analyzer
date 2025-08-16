from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Response, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import shutil
from pathlib import Path
import asyncio
import os
from crud import (
    create_resume,
    get_resume,
    check_existence
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
    BestResumeParms,
    ImprovementsInput,
    ModelUpdate
)
from utils import (
    embedding_model,
    hash_resume_content,
    load_ollama_model,
    unload_ollama_model
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
        
        hash = hash_resume_content(content=content)
        if check_existence(db, hash):
            continue

        add_task = asyncio.create_task(add_to_index(embedding_model, f_uuid, content))
        await create_resume(db, uuid=f_uuid, original_filename=original_filename, content=content, hash=hash)
        await add_task
    return Response(status_code=200)


@app.get("/improvements/")
async def get_resume_improvements(input: ImprovementsInput, db: Session = Depends(get_db)):
    # Inspect the resume and add to index and db if never seen before.
    if Path(input.resume).suffix.lower() not in (".pdf", ".docx"):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed.")
    original_filename = input.resume.filename
    ext = Path(original_filename).suffix.lower()

    f_uuid = str(uuid4())
    temp_path = FILES_DIR / f_uuid+ext
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(input.resume.file, buffer)
    try:
        content = read_resume(temp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {e}")
    
    hash = hash_resume_content(content=content)
    if not check_existence(db, hash):
        add_task = asyncio.create_task(add_to_index(embedding_model, f_uuid, content))
        await create_resume(db, uuid=f_uuid, original_filename=original_filename, content=content, hash=hash)
        await add_task

    # Parse the resume into sections
    # Parse the job description into sections
    # Create embeddings for each.
    # Manual keyword matching scores.
    # Embedding match ups.
    # Query LLM to improve the sections with low scores.
    # Future feature: Ask user if they would like to add these changes (separate route).
    
@app.get("/best")
async def get_best_resumes_for_job_description(params: BestResumeParms):
    if params.job_description is None or len(params.job_description)==0:
        raise HTTPException(status_code=400, detail="Must have a job description.")
    
    if params.count > 5:
        params.count = 5
    elif params.count <= 0:
        params.count = 1

    best = await query_index(
        job_description=params.job_description, 
        top_k=params.count,
    )

    return {"best" : best}


@app.get('/resume')
async def fetch_resume_file(file_uuid: str = Query(...), db: Session = Depends(get_db)):
    resume = await get_resume(db=db, uuid=file_uuid)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    file_path = Path(FILES_DIR) / f"{file_uuid}"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Resume file missing on disk")

    return FileResponse(
        file_path,
        filename=resume.original_filename,
        media_type="application/octet-stream"
    )

@app.post('/models')
async def set_model_info(md: ModelUpdate):
    if md.provider not in ["ollama", "anthropic", "openai"]:
        raise HTTPException(status_code=400, detail=f"Invalid Provider: {md.provider.capitalize()}")
    
    if md.model not in os.getenv(f"{md.model.upper()}_MODELS").split(","):
        raise HTTPException(status_code=400, detail=f"Model is not supported for {md.provider.capitalize()}: {md.model}")

    if md.api_key is None and md.provider != "ollama" and not os.getenv(f"{md.provider}_API_KEY"):
        raise HTTPException(status_code=400, detail=f"API key is not set for {md.provider.capitalize()}.")
    
    if os.getenv("MODEL_PROVIDER") == "ollama":
        await unload_ollama_model(os.getenv("MODEL"))

    if md.provider == "ollama":
        model_load_task = asyncio.create_task(load_ollama_model(md.model))
    
    os.environ["MODEL_PROVIDER"]=md.provider
    os.environ["MODEL"]=md.model
    if md.api_key is not None:
        os.environ[f"{md.provider.upper()}_API_KEY"] = md.api_key
    await model_load_task
    return Response()
    



    