from pydantic import BaseModel

class BestPdfsParms(BaseModel):
    job_description: str
    number: int