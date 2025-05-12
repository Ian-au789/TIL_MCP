import httpx
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")

async def generate_with_ollama(prompt: str) -> str:
    data = {"model": "mistral", "prompt": prompt, "stream": False}
    async with httpx.AsyncClient(timeout=60.0) as client:
        res = await client.post(OLLAMA_API_URL, json=data)
        res.raise_for_status()
        return res.json().get("response", "")
