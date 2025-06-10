from fastapi import APIRouter, Request, HTTPException
from tools.generate_problem import generate_problem_internal

call_router = APIRouter()

@call_router.post("/call")
async def handle_call(request: Request):
    try:
        print("[DEBUG] /call endpoint hit")

        body = await request.json()
        print(f"[DEBUG] Request body: {body}")

        tool = body.get("tool")
        input_data = body.get("input", {})
        print(f"[DEBUG] tool: {tool}, input: {input_data}")

        if tool == "generate_problem":
            result = await generate_problem_internal(input_data)
            print(f"[DEBUG] Generated problem result: {result}")
            return {"output": result}
        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {tool}")
    except Exception as e:
        print(f"[ERROR] Exception in /call: {str(e)}") 
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
