from fastapi import FastAPI
from mcp_instance import mcp
from tools import generate_mistral 
from routes.call_handler import handle_call
from middleware.request_logger import log_requests

app = FastAPI(title="Problem Generator MCP Server")

app.middleware("http")(log_requests)
app.post("/call")(handle_call)

@app.get("/")
def root():
    return {"status": "online", "model": "mistral"}

if __name__ == "__main__":
    import uvicorn
    print("[INFO] Starting FastAPI MCP server...")
    uvicorn.run("main:app", host="0.0.0.0", port=11500, reload=True)
