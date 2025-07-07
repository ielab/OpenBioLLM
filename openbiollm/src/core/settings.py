import os
from dotenv import load_dotenv

def configure_settings():
    load_dotenv()
    os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING", "true")
    os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
    os.environ["LANGSMITH_PROJECT_NAME"] = os.getenv("LANGSMITH_PROJECT_NAME", "OpenBioLLM-RAG")
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["USER_AGENT"] = "OpenBioLLM-RAG/1.0"

