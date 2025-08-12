from langchain_community.embeddings import HuggingFaceEmbeddings

def _normalize_text(text: str):
    pass

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
def load_embedding_model():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)