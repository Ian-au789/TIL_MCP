from fastapi import FastAPI
from router import call_router
from middleware import log_requests

app = FastAPI(title="Multi LLM MCP Server")
app.middleware("http")(log_requests)
app.include_router(call_router)

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "This is a multi-LLM enabled MCP server"
    }
