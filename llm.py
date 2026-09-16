import os
from openai import OpenAI

def get_client():    
    api_key = os.environ.get("OLLAMA_API_KEY", "ollama")
    return OpenAI(
        base_url='http://localhost:11434/v1/',
        api_key='ollama',
    )
