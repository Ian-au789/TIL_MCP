from mcp_instance import mcp
from services.ollama_client import generate_with_ollama
from services.utils import extract_json_from_text

@mcp.tool(
        name="generate_problem_mistral",
        description="Problem generator for simple option questions " \
        "such as based on a given definition choose the right word."
)
async def generate_problem_mistral(prompt: str) -> dict:
    print(f"[DEBUG] Generating problem with prompt: {prompt}")
    
    # Create a system prompt that instructs the LLM how to format the response
    system_prompt = """You are a problem generator for educational purposes. 
    Create a question based on the user's prompt. 
    The type of the question is 'select' if you created a multiple choice quesetion,
    or 'write' if you created a essay question.
    Your response must be in valid JSON format with the following structure:
    {
    "title": "Brief title of the problem",
    "content": "The full problem statement or question",
    "type": "select",
    "answer": "The correct answer for the question",
    "category": "Subject/Topic/Subtopic",
    }

    DO NOT include any explanations or text outside the JSON object.
    Also DO NOT make id field for this data. The server will created it automatically.
    Ensure your response is valid JSON that can be parsed programmatically.
    """

    # Combine the system prompt with the user's prompt
    full_prompt = f"{system_prompt}\n\nUser Request: {prompt}"

    try:
        response = await generate_with_ollama(full_prompt)
        print(f"[DEBUG] Raw LLM response: {response[:]}...")

        problem_data = await extract_json_from_text(response)
        
        # Validate the problem data structure
        required_fields = ["title", "content", "type", "options", "answer"]
        for field in required_fields:
            if field not in problem_data:
                problem_data[field] = f"Missing {field}" if field != "options" else ["Option 1", "Option 2"]
        
        # Make sure options is a list
        if not isinstance(problem_data.get("options", []), list):
            problem_data["options"] = ["Option 1", "Option 2", "Option 3", "Option 4"]
            
        # Make sure answer is in options
        if problem_data.get("answer") not in problem_data.get("options", []):
            problem_data["answer"] = problem_data["options"][0]

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

