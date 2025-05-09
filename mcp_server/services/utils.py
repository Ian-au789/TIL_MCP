import json

async def extract_json_from_text(text: str) -> dict:
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "title": "JSON Error",
            "content": "Could not parse LLM response.",
            "type": "select",
            "options": ["Error"],
            "answer": "Error",
            "category": "Error"
        }
