import httpx
from config import UPSTAGE_API_KEY

async def generate(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {UPSTAGE_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "solar-1-pro-chat",  # 또는 "solar-1-pro-chat" (유료 사용 시)
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.upstage.ai/v1/solar/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
