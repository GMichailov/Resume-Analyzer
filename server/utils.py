from langchain_community.embeddings import HuggingFaceEmbeddings
import hashlib
import requests
import os
import json
import boto3

def hash_resume_content(content: str) -> str:
    norm = content.strip().encode('utf-8')
    return hashlib.sha1(norm).hexdigest()

async def load_ollama_model(model: str):
    # Run indefinitely until termination or switched.
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": "", "stream": False, "keep_alive": -1}
    )

async def unload_ollama_model(model: str):
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": "", "stream": False, "keep_alive": 0}
    )

def query_router(prompt):
    provider = os.getenv("MODEL_PROVIDER")
    if provider not in ["ollama", "anthropic","openai"]:
        raise ValueError("Invalid provider.")
    model = os.getenv("MODEL")
    if len("model") == 0:
        raise ValueError(f"Model not set for {provider}.")
    if provider == "ollama":
        return query_ollama(model, prompt)
    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(f"Api key not set for OpenAI.")
        return query_openai(model, prompt)
    else:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(f"Api key not set for Anthropic.")
        return query_anthropic(model, prompt)

def query_ollama(model, prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    data = resp.json()

    return data.get("response", "")

def query_openai(model: str, prompt: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def query_anthropic(model: str, prompt: str) -> str:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }

    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)