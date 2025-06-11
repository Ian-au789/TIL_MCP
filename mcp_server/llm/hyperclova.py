from config import CLOVA_API_KEY
import httpx


async def generate(prompt: str) -> str:
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {CLOVA_API_KEY}",
    }
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "topP": 0.8,
        "temperature": 0.7
    }
    async with httpx.AsyncClient() as client:
        res = await client.post("https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-DASH-001", headers=headers, json=payload)
        res.raise_for_status()
        return res.json()["result"]["message"]["content"]


#"X-NCP-CLOVASTUDIO-REQUEST-ID": "cb74c8fb916a4ebbba73c47fe99e8c83"
# 유효 주소 : https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003
# 다음 목표 : HCX-005, HCX-DASH