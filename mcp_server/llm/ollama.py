from config import OLLAMA_URL, OLLAMA_MODEL
import httpx

async def generate(prompt: str) -> str:
    data = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    async with httpx.AsyncClient() as client:
        res = await client.post(OLLAMA_URL, json=data)
        res.raise_for_status()
        return res.json()["response"]
