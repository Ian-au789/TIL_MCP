from config import CLOVA_API_KEY
import httpx


async def generate(prompt: str) -> str:
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {CLOVA_API_KEY}",
    }
    # payload = {
    #     "messages": [{"role": "user", "content": prompt}],
    #     "topP": 0.8,
    #     "temperature": 0.7
    # }
    # async with httpx.AsyncClient() as client:
    #     res = await client.post("https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-DASH-001", headers=headers, json=payload)
    #     res.raise_for_status()
    #     return res.json()["result"]["message"]["content"]

    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "topP": 0.8,
        "temperature": 0.7,
        "maxTokens": 512
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(
                "https://clovastudio.stream.ntruss.com/testapp/v3/chat-completions/HCX-005",
                headers=headers,
                json=payload
            )
            res.raise_for_status()
            data = res.json()
            return data["result"]["message"]["content"]
        
    except httpx.HTTPStatusError as e:
        print("[ERROR] 상태코드:", e.response.status_code)
        print("[ERROR] 응답 내용:", e.response.text)
    except Exception as e:
        print("[ERROR] 예외 발생:", str(e))
    return None


#"X-NCP-CLOVASTUDIO-REQUEST-ID": "cb74c8fb916a4ebbba73c47fe99e8c83"
# 유효 주소 : https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003
# 다음 목표 : HCX-005, HCX-DASH-02
# https://clovastudio.stream.ntruss.com/testapp/v1/completions/HCX-005
# https://clovastudio.stream.ntruss.com/testapp/v3/chat-completions/HCX-DASH-002
