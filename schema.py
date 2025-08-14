from pydantic import BaseModel
from fastapi import File

class BestResumeParms(BaseModel):
    job_description: str
    count: int

class BestResumeRet(BaseModel):
    resumes: list[File]