from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import asyncio
import numpy as np

from annoy import AnnoyIndex

SQLALCHEMY_DATABASE_URL = "sqlite:///./resumes.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

EMBEDDING_DIM = 384
TREES = 10

def create_index():
    index_save_path = Path("uploads" / "index.ann")
    if not index_save_path.exists():
        index = AnnoyIndex(EMBEDDING_DIM, "angular")
        index.save(index_save_path)


async def load_index():
    return AnnoyIndex.load(str(Path("uploads/index.ann")))


async def add_to_index(embedding_model, resume_uuid: str, resume_content):
    embedding_task = asyncio.create_task(embedding_model.encode, resume_content, convert_to_numpy=True)
    index = await load_index()
    embedding = await embedding_task
    index.add_item(resume_uuid, embedding.tolist())
    index.build(TREES)
    index.save(str(Path("uploads" / "index.ann")))
    


