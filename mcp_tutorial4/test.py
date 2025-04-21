import requests

url = "https://63b8-210-217-23-139.ngrok-free.app/tools/define"

try:
    response = requests.post(url, timeout=5)
    response.raise_for_status()
    data = response.json()
    print("🛠️ 사용 가능한 MCP 툴 목록:")
    for tool in data.get("tools", []):
        print(f"- 이름: {tool.get('name')}")
        print(f"  설명: {tool.get('description')}\n")
except Exception as e:
    print(f"❌ MCP 서버 접속 실패: {e}")
