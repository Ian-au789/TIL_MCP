import time
import random
from fastapi import Request

async def log_requests(request: Request, call_next):
    req_id = random.randint(1000, 9999)
    start = time.time()
    print(f"[{req_id}] {request.method} {request.url}")

    if request.method in ["POST", "PUT"]:
        body = await request.body()
        print(f"[{req_id}] Body: {body[:200]}...")

    response = await call_next(request)
    duration = time.time() - start
    print(f"[{req_id}] Done in {duration:.3f}s with {response.status_code}")
    return response
