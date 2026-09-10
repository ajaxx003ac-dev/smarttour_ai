import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smarttour.db")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
LLM_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-5.6-luna")
