from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from dotenv import load_dotenv
import os
import httpx

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

async def ask_mistral(question: str) -> str:
    payload = {
        "model": "mistral",
        "prompt": question,
        "stream": False
    }
    try:
        response = httpx.post(f"{OLLAMA_URL}/api/generate", json=payload)
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"Error calling Mistral: {e}"

@mcp.tool_schema
def tool_schemas():
    return [
        {
            "name": "ask_mistral",
            "description": "Ask a general question to Mistral",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"}
                },
                "required": ["question"]
            }
        }
    ]

@mcp.dispatch
async def dispatch_tool(tool_call: dict) -> str:
    name = tool_call.get("name")
    args = tool_call.get("arguments", {})
    if name == "ask_mistral" and "question" in args:
        return await ask_mistral(args["question"])
    return "Invalid tool or missing arguments"

mcp.mount()
mcp.setup_server()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
