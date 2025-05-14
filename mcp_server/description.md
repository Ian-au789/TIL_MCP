# 📁 MCP 기반 문제 생성 서버 - 디렉토리 구조 설명

이 프로젝트는 FastAPI와 FastMCP를 기반으로, 로컬 LLM(Ollama의 Mistral)과 클라우드 LLM(GPT 등)을 연동하여 문제를 자동 생성하는 에이전트형 시스템입니다.  
다음은 디렉토리 구조와 각 파일/모듈의 역할을 정리한 문서입니다.

---

## 📂 프로젝트 구조

mcp_server/
├── main.py # FastAPI 앱 실행 진입점
├── mcp_instance.py # MCP 인스턴스 정의 및 툴 공유용 모듈
│
├── tools/ # MCP 툴(LLM 호출 기능) 정의
│ └── generate_mistral.py # 로컬 Mistral을 사용한 문제 생성 툴
│
├── services/ # LLM 통신 및 데이터 처리 로직
│ ├── ollama_client.py # Ollama API 호출 (로컬 LLM용)
│ └── utils.py # JSON 파싱 등 공통 유틸리티 함수
│
├── routes/ # HTTP 라우팅 핸들러
│ └── call_handler.py # /call 엔드포인트에서 MCP 툴 실행 분기 처리
│
├── middleware/ # 요청/응답 로깅 등의 중간 처리기
│ └── request_logger.py # HTTP 요청 로그 출력용 미들웨어


---

## 📄 주요 파일 설명

### 🔹 `main.py`
- FastAPI 서버 실행을 위한 엔트리 포인트입니다.
- MCP 툴들을 로드하고 `/call` 등의 엔드포인트를 연결합니다.
- 개발 중에는 `uvicorn.run()`을 통해 직접 서버를 실행합니다.

### 🔹 `mcp_instance.py`
- `FastMCP` 인스턴스를 생성하여 프로젝트 전체에 공유합니다.
- 순환 참조(circular import)를 방지하기 위해 별도 분리되어 있습니다.

---

## 📁 tools/

### 🔸 `generate_mistral.py`
- MCP의 `@mcp.tool()` 데코레이터를 이용해 툴을 정의합니다.
- 사용자 프롬프트를 받아 Mistral에게 전달하고 JSON 문제 데이터를 반환합니다.
- 유효성 검사 및 fallback 처리도 포함되어 있습니다.

---

## 📁 services/

### 🔸 `ollama_client.py`
- Ollama API(`localhost:11434`)를 통해 로컬 LLM에 프롬프트를 전송합니다.
- 응답 스트리밍 없이 전체 응답을 `httpx.AsyncClient`로 수신합니다.

### 🔸 `utils.py`
- LLM 응답에서 JSON 형식을 추출하거나 fallback 문제를 구성합니다.
- 향후 GPT나 Claude용 파서가 추가될 수도 있습니다.

---

## 📁 routes/

### 🔸 `call_handler.py`
- `/call` 엔드포인트에서 전달받은 툴 이름에 따라 적절한 MCP 툴을 실행합니다.
- JSON 요청 형식을 검증하고 예외 처리를 포함합니다.

---

## 📁 middleware/

### 🔸 `request_logger.py`
- 모든 HTTP 요청/응답에 대해 로그를 출력합니다.
- 요청 ID, 요청 body, 처리 시간 등을 출력하여 디버깅에 활용됩니다.

---

## 🧠 확장 시 구조 예시

| 기능 추가          | 추가 위치 예시                         |
|-------------------|----------------------------------------|
| GPT 기반 문제 생성 | `tools/generate_gpt.py`                |
| 툴 자동 분기 로직   | `@mcp.dispatch()` in `dispatch.py`     |
| PostgreSQL 저장 기능| `services/db_manager.py`              |
| Swagger-like 툴 조회 | `/tools/define` FastMCP 기본 엔드포인트 사용 |

---

## 📌 실행 방법

```bash
$ cd mcp_server
$ python main.py
$ uvicorn main:app --reload --port 11500

# 면접 끝날 때까지 한동안 휴업