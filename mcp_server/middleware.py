import random
import time
from fastapi import Request

async def log_requests(request: Request, call_next):
    request_id = random.randint(1000, 9999)
    print(f"[{request_id}] {request.method} {request.url}")
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    print(f"[{request_id}] Completed in {duration:.2f}s with {response.status_code}")
    return response
