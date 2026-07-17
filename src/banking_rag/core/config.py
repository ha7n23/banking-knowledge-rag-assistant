import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")

RAW_DOCS_DIR = PROJECT_ROOT / "data" / "raw_docs"
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma_db"
EVALUATION_FILE = PROJECT_ROOT / "evaluation" / "evaluation_questions.json"
EVALUATION_REPORTS_DIR = PROJECT_ROOT / "evaluation" / "reports"

COLLECTION_NAME = "banking_knowledge_base"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 900
CHUNK_OVERLAP = 120
TOP_K = 3

APP_NAME = os.getenv("APP_NAME", "Banking Knowledge RAG Assistant")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")