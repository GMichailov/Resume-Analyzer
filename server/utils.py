from langchain_community.embeddings import HuggingFaceEmbeddings
import hashlib

def hash_resume_content(content: str) -> str:
    norm = content.strip().encode('utf-8')
    return hashlib.sha1(norm).hexdigest()

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)