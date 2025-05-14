from fastapi import Request, HTTPException
from tools.generate_mistral import generate_problem_mistral
from tools.generate_gpt import generate_problem_with_gpt

async def handle_call(request: Request):
    try:
        data = await request.json()
        tool = data.get("tool")
        input_data = data.get("input", {})
        if tool == "generate_problem_mistral":
            result = await generate_problem_mistral(input_data.get("prompt", ""))
            return {"output": result}
        
        elif tool == "generate_problem_with_gpt":
            result = await generate_problem_with_gpt(input_data.get("prompt", ""))
            return {"output": result}

        else:
            raise HTTPException(status_code=400, detail="Unknown tool")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Call failed: {str(e)}")
