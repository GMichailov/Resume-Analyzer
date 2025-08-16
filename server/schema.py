from pydantic import BaseModel
from fastapi import File

class ImprovementsInput(BaseModel):
    resume : File 
    job_description: str | None
    comments: str | None

class BestResumeParms(BaseModel):
    job_description: str
    count: int

class BestResumeRet(BaseModel):
    resumes: list[File]

class ModelUpdate(BaseModel):
    provider: str
    model: str
    api_key: str | None