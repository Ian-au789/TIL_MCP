from fastapi import FastAPI, Request, HTTPException
from fastmcp import FastMCP
from typing import Dict, Any, Optional, List
import uvicorn
import random
import time
import json
import httpx
import asyncio

# Create FastAPI application
app = FastAPI(title="Problem Generator MCP Server")

# Create FastMCP instance (without mounting)
mcp = FastMCP("problem-generator-mcp")

# Ollama API configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"  # The model name you've downloaded via Ollama

async def generate_with_ollama(prompt: str) -> str:
    """
    Send a prompt to the Ollama API and get the generated response.
    """
    request_data = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(OLLAMA_API_URL, json=request_data)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except httpx.RequestError as e:
            print(f"[ERROR] Request to Ollama API failed: {str(e)}")
            raise Exception(f"Failed to communicate with Ollama API: {str(e)}")

async def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Extract JSON object from text response.
    """
    # Try to find JSON object in the response
    try:
        # Look for text between curly braces
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = text[start_idx:end_idx]
            return json.loads(json_str)
        else:
            # If no JSON found, try to parse the whole text
            return json.loads(text)
    except json.JSONDecodeError:
        print(f"[ERROR] Failed to extract JSON from: {text}")
        # Return a default problem if JSON extraction fails
        return {
            "title": "JSON Parsing Error",
            "content": "The LLM response could not be parsed as JSON.",
            "type": "select",
            "options": ["Error in response format"],
            "answer": "Error in response format",
            "category": "Error",
            "difficulty": "N/A"
        }

# Define the problem generation tool
@mcp.tool()
async def generate_problem(prompt: str) -> Dict[str, Any]:
    """
    Use local LLM to generate a problem based on the prompt.
    """
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
  "type": "Either select or write",
  "answer": "The correct answer for the question",
  "category": "Subject/Topic/Subtopic",
}

DO NOT include any explanations or text outside the JSON object.
Ensure your response is valid JSON that can be parsed programmatically.
"""

    # Combine the system prompt with the user's prompt
    full_prompt = f"{system_prompt}\n\nUser Request: {prompt}"
    
    try:
        # Get response from Ollama
        llm_response = await generate_with_ollama(full_prompt)
        print(f"[DEBUG] Raw LLM response: {llm_response[:]}...")
        
        # Extract JSON from the response
        problem_data = await extract_json_from_text(llm_response)
        
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
        print(f"[ERROR] Problem generation failed: {str(e)}")
        # Fallback to dummy data if LLM generation fails
        return {
            "title": "LLM Error Fallback",
            "content": f"An error occurred while generating a problem: {str(e)}",
            "type": "select",
            "options": [
                "Retry with a different prompt",
                "Check Ollama server status",
                "Use more specific prompt",
                "Contact system administrator"
            ],
            "answer": "Check Ollama server status",
            "category": "Error/Fallback",
            "difficulty": "N/A"
        }

# Log middleware for debugging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = random.randint(1000, 9999)
    start_time = time.time()
    
    print(f"[{request_id}] Request: {request.method} {request.url}")
    
    try:
        # Get request body for POST/PUT requests
        if request.method in ["POST", "PUT"]:
            body_bytes = await request.body()
            if body_bytes:
                body_text = body_bytes.decode()
                # Trim long bodies for logging
                if len(body_text) > 1000:
                    body_text = body_text[:1000] + "... [truncated]"
                print(f"[{request_id}] Request body: {body_text}")
    except Exception as e:
        print(f"[{request_id}] Failed to log request body: {str(e)}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    print(f"[{request_id}] Response status: {response.status_code}")
    print(f"[{request_id}] Process time: {process_time:.4f} seconds")
    
    return response

# Custom endpoint to handle MCP calls
@app.post("/call")
async def handle_call(request: Request):
    """
    Custom endpoint to handle calls from the FastAPI client
    """
    try:
        # Parse request body
        body = await request.json()
        
        # Extract tool name and input
        tool_name = body.get("tool")
        input_data = body.get("input", {})
        
        print(f"[CALL] Handling request for tool: {tool_name}")
        print(f"[CALL] Input data: {json.dumps(input_data, ensure_ascii=False)}")
        
        # Handle generate_problem tool
        if tool_name == "generate_problem":
            prompt = input_data.get("prompt", "")
            result = await generate_problem(prompt)
            return {"output": result}
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown tool: {tool_name}"
            )
            
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, 
            detail="Invalid JSON in request body"
        )
    except Exception as e:
        print(f"[ERROR] Exception in handle_call: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing request: {str(e)}"
        )

# Root endpoint for health check
@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Problem Generator MCP Server with Local LLM",
        "model": OLLAMA_MODEL,
        "endpoints": {
            "call": "/call"
        }
    }

# Endpoint to test LLM connectivity
@app.get("/test-llm")
async def test_llm():
    """
    Test the connection to the Ollama LLM.
    """
    try:
        result = await generate_with_ollama("Generate a short greeting message.")
        return {
            "status": "success",
            "message": "Successfully connected to Ollama LLM",
            "model": OLLAMA_MODEL,
            "sample_response": result[:200] + ("..." if len(result) > 200 else "")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to connect to Ollama LLM: {str(e)}"
        }

# Run the server
if __name__ == "__main__":
    print(f"Starting MCP Server with {OLLAMA_MODEL} LLM integration on port 11500...")
    uvicorn.run(app, host="0.0.0.0", port=11500)