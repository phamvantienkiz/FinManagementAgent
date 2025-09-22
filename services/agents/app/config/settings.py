import os
from dotenv import load_dotenv
from pathlib import Path

# Build an absolute path to the .env file from the location of this settings file
# This makes the .env loading independent of the current working directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    # API Keys
    BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PROTONX_API_KEY = os.getenv("PROTONX_API_KEY")
    
    # Model configurations (base names; provider prefix added in BaseAgent)
    # Prefer a widely available, stable model id for both LangChain and LiteLLM
    GEMINI_MODEL = "gemini-1.5-flash"
    FINANCE_MODEL = "deepseek-ai/DeepSeek-V2-Lite"
    
    # CrewAI configurations
    VERBOSE = True
    MAX_ITERATIONS = 3

settings = Settings()
