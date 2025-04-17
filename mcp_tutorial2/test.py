from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

app = FastAPI()
mcp = FastApiMCP(app)

print("✅ Available attributes in FastApiMCP:")
for attr in dir(mcp):
    if not attr.startswith("_"):
        print("-", attr)
