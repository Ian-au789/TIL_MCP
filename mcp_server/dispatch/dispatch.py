from mcp_instance import mcp

@mcp.dispatch()
def choose_tool(prompt: str) -> str:
    """
    Dispatch tool based on user prompt.
    Let Mistral decide which tool (e.g., GPT or Mistral) should generate the problem.
    """
    return f"""
    You are a tool router. Your task is to select the most appropriate tool to handle a user's problem generation request.

    Available tools:
    - generate_problem_mistral: Fast and simple problem generation using a local LLM (Mistral). Suitable for basic, easy, or low-cost problems.
    - generate_problem_with_gpt: Uses GPT-4 for more complex, creative, or high-quality problem generation. Suitable for difficult or nuanced questions.

    Given the user's prompt:
    "{prompt}"

    Select and return only the **tool name** as one of the following:
    - generate_problem_mistral
    - generate_problem_with_gpt
    Do not return any explanation or text. Just return the exact tool name.
    """
