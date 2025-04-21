import requests
import httpx
import json
from typing import List, Dict, Any, Optional

# MCP 서버에서 툴 정의를 수집하는 함수
def gather_mcp_tools(server_urls: List[str]) -> List[Dict[str, Any]]:
    tools = []
    for base_url in server_urls:
        try:
            res = requests.post(f"{base_url}/tools/define", timeout=5)
            res.raise_for_status()
            for tool in res.json().get("tools", []):
                tools.append({"server": base_url, **tool})
        except Exception as e:
            print(f"⚠️ {base_url} 접속 실패: {e}")
    return tools

# 이름으로 툴 선택하기
def select_tool_by_name(tools: List[Dict[str, Any]], target_name: str) -> Optional[Dict[str, Any]]:
    for tool in tools:
        if tool.get("name") == target_name:
            return tool
    return None

# MCP 툴 실행 함수
def run_tool(tool: Dict[str, Any], arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        res = requests.post(
            f"{tool['server']}/tools/call",
            json={"name": tool["name"], "arguments": arguments},
            timeout=30
        )
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": str(e)}

# LLM 호출 함수 (Mistral via Ollama)
def call_llm_with_prompt(prompt: str) -> str:
    payload = {
        "model": "mistral:latest",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = httpx.post("http://localhost:11434/api/generate", json=payload, timeout=30)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"LLM 호출 오류: {e}"

# 사용자 요청과 툴 목록을 기반으로 LLM에게 툴 선택 요청
def ask_llm_to_select_tool(prompt: str, tools: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    tool_descriptions = "\n".join([
        f"- {tool['name']}: {tool['description']}" for tool in tools
    ])

    full_prompt = f"""
다음은 사용 가능한 툴 목록입니다:

{tool_descriptions}

사용자의 요청:
\"{prompt}\"

위 요청을 처리하기 위해 가장 적절한 툴 하나를 선택하고, 필요한 arguments를 JSON 형식으로 반환해 주세요.

출력 형식 예:
{{
  "name": "commit_if_needed",
  "arguments": {{}}
}}

오직 JSON 형식만 출력해 주세요.
"""
    raw_response = call_llm_with_prompt(full_prompt)

    try:
        return json.loads(raw_response)
    except Exception as e:
        print(f"❌ JSON 파싱 실패: {e}")
        print("🔎 LLM 응답 원문:", raw_response)
        return None

# 전체 실행 흐름
def main():
    print("🚀 MCP 클라이언트 시작됨")
    mcp_servers = [
        "https://63b8-210-217-23-139.ngrok-free.app"
    ]

    tools = gather_mcp_tools(mcp_servers)

    user_prompt = "오늘 커밋이 없다면 자동으로 커밋하고 푸시해줘, 사용 가능한 여러개의 툴 중에 우선적으로 batch_commit을 사용해서 커밋하도록 해봐"
    plan = ask_llm_to_select_tool(user_prompt, tools)

    if plan:
        selected_tool = select_tool_by_name(tools, plan["name"])
        if selected_tool:
            result = run_tool(selected_tool, plan["arguments"])
            print("\n✅ 툴 실행 결과:", result)
        else:
            print("❌ 선택된 툴을 MCP 서버 목록에서 찾을 수 없습니다.")
    else:
        print("❌ LLM으로부터 적절한 툴 플랜을 받지 못했습니다.")

if __name__ == "__main__":
    main()
