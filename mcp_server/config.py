import os
from dotenv import load_dotenv


load_dotenv()
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLOVA_API_KEY = os.getenv("CLOVA_API_KEY")
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")