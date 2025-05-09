from fastapi import Request, HTTPException
from tools.generate_mistral import generate_problem

async def handle_call(request: Request):
    try:
        data = await request.json()
        tool = data.get("tool")
        input_data = data.get("input", {})
        if tool == "generate_problem":
            result = await generate_problem(input_data.get("prompt", ""))
            return {"output": result}
        else:
            raise HTTPException(status_code=400, detail="Unknown tool")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Call failed: {str(e)}")
