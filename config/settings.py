OLLAMA_CONFIG = {
    "model": "llama2",
    "context_window": 4096,
    "temperature": 0.7,
    "max_tokens": 512
}

CHROMA_CONFIG = {
    "persist_directory": "./data/chroma",
    "collection_name": "pronto_4gl",
    "embedding_dimension": 384
}

API_CONFIG = {
    "host": "localhost",
    "port": 8000,
    "workers": 4
}
