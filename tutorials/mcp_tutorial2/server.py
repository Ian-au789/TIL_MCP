from fastapi import FastAPI, Query
from fastapi_mcp import FastApiMCP
from dotenv import load_dotenv
import os, httpx, uvicorn

load_dotenv()
app = FastAPI()

# MCP 설정
mcp = FastApiMCP(
    app,
    name="ask-mistral-agent",
    description="Ask questions to Mistral via Claude and MCP",
    base_url="http://localhost:8000"
)

# Ollama 서버 주소 설정
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# 기본 라우트: 서버 상태 확인용
@app.get("/")
async def root():
    return {"message": "MCP Ask-Mistral Agent is live!"}

# 핵심 기능: 질문을 Mistral에게 보내고 응답 받기
@app.get("/ask", operation_id="ask_mistral", description="Ask a question to Mistral")
async def ask_mistral_endpoint(question: str = Query(..., description="질문 내용")):
    payload = {
        "model": "mistral",
        "prompt": question,
        "stream": False
    }
    try:
        res = httpx.post(f"{OLLAMA_URL}/api/generate", json=payload)
        return {"response": res.json().get("response", "").strip()}
    except Exception as e:
        return {"error": str(e)}

# MCP 서버 구성
mcp.mount()
mcp.setup_server()

# 서버 실행
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
