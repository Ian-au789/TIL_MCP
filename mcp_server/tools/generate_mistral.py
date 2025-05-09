from mcp_instance import mcp
from services.ollama_client import generate_with_ollama
from services.utils import extract_json_from_text

@mcp.tool()
async def generate_problem(prompt: str) -> dict:
    system_prompt = "..."
    full_prompt = f"{system_prompt}\n\nUser Request: {prompt}"

    try:
        response = await generate_with_ollama(full_prompt)
        problem_data = await extract_json_from_text(response)
        # 필드 보정 로직 추가
        return problem_data
    except Exception as e:
        return {
            "title": "LLM Error",
            "content": f"Failed to generate problem: {e}",
            "type": "select",
            "options": ["Retry", "Contact admin"],
            "answer": "Retry",
            "category": "Error"
        }
