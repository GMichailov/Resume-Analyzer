from pydantic import BaseModel

class BestPdfsParms(BaseModel):
    job_description: str
    count: int