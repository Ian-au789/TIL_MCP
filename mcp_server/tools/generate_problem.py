from fastmcp import FastMCP
from typing import Dict, Any
from utils.json_extractor import extract_json_from_text
from llm import ollama, chatgpt, hyperclova, solar

mcp = FastMCP("multi-llm-problem-gen")

# 내부에서 호출 가능한 함수
async def generate_problem_internal(input: Dict[str, Any]) -> Dict[str, Any]:
    prompt = input.get("prompt", "")
    llm = input.get("llm", "")

    system_prompt = '''
                    당신은 교육용 문제를 생성하는 인공지능입니다.  
                    사용자의 요청에 따라 문제를 생성하세요.  
                    문제 유형은 다음 중 하나입니다:  
                    - 객관식 문제일 경우: "select"  
                    - 서술형 문제일 경우: "write"

                    당신의 응답은 반드시 아래 형식의 유효한 JSON 객체여야 하며, 그 외 설명이나 텍스트는 절대 포함하지 마세요:

                    {
                    "title": "문제의 간단한 제목",
                    "content": "문제의 전체 내용 또는 질문",
                    "type": "select 또는 write 중 하나",
                    "answer": "문제의 정답",
                    "category": "과목/주제/세부주제 형식의 분류 (예: 수학/확률과통계/조건부확률)"
                    }

                    만약 "select" 유형의 문제를 만들었다면, content 안에 반드시 보기 4개를 아래와 같이 포함해야 합니다:

                    1) 보기1  
                    2) 보기2  
                    3) 보기3  
                    4) 보기4  

                    "answer" 필드는 위 보기 중 정답 번호 하나로 작성하세요 (예: "2").

                    주의사항:
                    - 절대 JSON 외의 설명이나 텍스트를 포함하지 마세요.
                    - id 필드는 만들지 마세요. 서버에서 자동 생성됩니다.
                    - 응답은 반드시 파싱 가능한 JSON이어야 합니다.
                    '''

    full_prompt = f"{system_prompt}\n\n{prompt}"

    try:
        if llm == "ollama":
            raw = await ollama.generate(full_prompt)
        elif llm == "chatgpt":
            raw = await chatgpt.generate(full_prompt)
        elif llm == "hyperclova":
            raw = await hyperclova.generate(full_prompt)
        elif llm == "solar":
            raw = await solar.generate(full_prompt)
        else:
            raise ValueError(f"Unsupported LLM: {llm}")

        return await extract_json_from_text(raw)

    except Exception as e:
        print(f"[ERROR] LLM 호출 실패: {str(e)}")
        return None


# MCP에서 사용할 툴 등록
@mcp.tool()
async def generate_problem(input: Dict[str, Any]) -> Dict[str, Any]:
    return await generate_problem_internal(input)

# 시스템 프롬프트 (영어)
"""You are a problem generator for educational purposes. 
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

    If you choose select type, the content should include 4 answer options in 1, 2, 3, 4. The answer should be a single number.
    DO NOT include any explanations or text outside the JSON object.
    Also DO NOT make id field for this data. The server will created it automatically.
    Ensure your response is valid JSON that can be parsed programmatically.
    """

# 시스템 프롬프트 (한국어)
'''
당신은 교육용 문제를 생성하는 인공지능입니다.  
사용자의 요청에 따라 문제를 생성하세요.  
문제 유형은 다음 중 하나입니다:  
- 객관식 문제일 경우: "select"  
- 서술형 문제일 경우: "write"

당신의 응답은 반드시 아래 형식의 **유효한 JSON 객체**여야 하며, 그 외 설명이나 텍스트는 절대 포함하지 마세요:

{
  "title": "문제의 간단한 제목",
  "content": "문제의 전체 내용 또는 질문",
  "type": "select 또는 write 중 하나",
  "answer": "문제의 정답",
  "category": "과목/주제/세부주제 형식의 분류 (예: 수학/확률과통계/조건부확률)"
}

만약 "select" 유형의 문제를 만들었다면, content 안에 반드시 보기 4개를 아래와 같이 포함해야 합니다:

1) 보기1  
2) 보기2  
3) 보기3  
4) 보기4  

"answer" 필드는 위 보기 중 정답 번호 하나로 작성하세요 (예: "2").

주의사항:
- 절대 JSON 외의 설명이나 텍스트를 포함하지 마세요.
- id 필드는 만들지 마세요. 서버에서 자동 생성됩니다.
- 응답은 반드시 파싱 가능한 JSON이어야 합니다.
'''