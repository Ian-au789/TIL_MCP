import json
from typing import Dict, Any

async def extract_json_from_text(text: str) -> Dict[str, Any]:
    try:
        start, end = text.find("{"), text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
        return json.loads(text)  # fallback
    except json.JSONDecodeError:
        return {
            "title": "Parsing Error",
            "content": "Invalid JSON returned",
            "type": "select",
            "options": ["Check prompt", "Retry", "Contact admin"],
            "answer": "Retry",
            "category": "Error"
        }
