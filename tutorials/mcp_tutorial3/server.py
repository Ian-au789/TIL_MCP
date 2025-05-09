from fastapi import FastAPI, Query
from fastapi_mcp import FastApiMCP
from dotenv import load_dotenv
import os, httpx, uvicorn

load_dotenv()
app = FastAPI()

mcp = FastApiMCP(
    app,
    name="ask-mistral-agent",
    description="Ask questions to Mistral via Claude and MCP",
    base_url="http://localhost:8000"
)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

@app.get("/")
async def root():
    return {"message": "MCP Ask-Mistral Agent is live!"}

@mcp.tool(
    name="ask_mistral",
    description="Ask a general question to Mistral"
)
async def ask_mistral(question: str):
    payload = {
        "model": "mistral:latest",
        "prompt": question,
        "stream": False,
    }
    try:
        res = httpx.post(f"{OLLAMA_URL}/api/generate", json=payload)
        return res.json().get("response", "").strip()
    except Exception as e:
        return f"Error: {e}"

mcp.mount()
mcp.setup_server()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
