from langchain_community.embeddings import HuggingFaceEmbeddings

def _normalize_text(text: str):
    pass

embedding_model = None

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
def load_embedding_model():
    global embedding_model
    embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)