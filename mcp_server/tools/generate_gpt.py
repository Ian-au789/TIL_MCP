from openai import AsyncOpenAI
from mcp_instance import mcp
from services.utils import extract_json_from_text
import os

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@mcp.tool(
        name="generate_problem_with_gpt",
        description="Problem generator for intermediate/advanced questions for both option and writing questions"
)
async def generate_problem_with_gpt(prompt: str) -> dict:
    system_prompt = """You are a problem generator for educational purposes. 
    Create a question based on the user's prompt. 
    The type of the question is 'select' if you created a multiple choice quesetion,
    or 'write' if you created a essay question.
    Your response must be in valid JSON format with the following structure:
    {
    "title": "Brief title of the problem",
    "content": "The full problem statement or question",
    "type": "Either select or write",
    "answer": "The correct answer for the question",
    "category": "Subject/Topic/Subtopic",
    }

    DO NOT include any explanations or text outside the JSON object.
    Also DO NOT make id field for this data. The server will created it automatically.
    Ensure your response is valid JSON that can be parsed programmatically.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    try:
        res = await client.chat.completions.create(
            model="gpt-4-mini",
            messages=messages,
            temperature=0.7
        )
        response_text = res.choices[0].message.content
        return await extract_json_from_text(response_text)
    except Exception as e:
        return {
            "title": "GPT Error",
            "content": str(e),
            "type": "Error",
            "answer": "Retry",
            "category": "Error",
        }