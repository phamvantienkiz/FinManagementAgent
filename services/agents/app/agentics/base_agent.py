import os
from crewai import Agent
from app.config import settings

class BaseAgent:
    def __init__(self, llm_type="gemini"):
        # Instead of creating the LLM object here, we just store the type
        # and the corresponding model name from settings.
        if llm_type == "gemini":
            self.llm_provider = "google"
            self.model_name = settings.GEMINI_MODEL
            # Map GOOGLE_API_KEY from settings to the env var LiteLLM expects
            if settings.GOOGLE_API_KEY and not os.environ.get("GEMINI_API_KEY"):
                os.environ["GEMINI_API_KEY"] = settings.GOOGLE_API_KEY
            # Also set GOOGLE_API_KEY env var for libraries that reference it directly
            if settings.GOOGLE_API_KEY and not os.environ.get("GOOGLE_API_KEY"):
                os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
        else:
            # This part can be expanded for other providers like HuggingFace
            self.llm_provider = "huggingface"
            self.model_name = settings.FINANCE_MODEL
            # Ensure HF token available for LiteLLM if needed
            if settings.HUGGINGFACE_API_KEY and not os.environ.get("HUGGINGFACE_API_KEY"):
                os.environ["HUGGINGFACE_API_KEY"] = settings.HUGGINGFACE_API_KEY
    
    def create_agent(self, role, goal, backstory, tools, verbose=True):
        """Create a CrewAI Agent using LiteLLM-compatible model strings.

        We pass a model id string (e.g., "gemini/gemini-1.5-flash") so CrewAI/LiteLLM
        can resolve the provider automatically using environment variables
        like GOOGLE_API_KEY or HUGGINGFACE_API_KEY.
        """

        # Build LiteLLM model identifier
        llm_model = self.model_name
        if self.llm_provider == "google":
            # Ensure provider prefix for LiteLLM
            if not llm_model.startswith("gemini/"):
                llm_model = f"gemini/{llm_model}"
        elif self.llm_provider == "huggingface":
            if not llm_model.startswith("huggingface/"):
                llm_model = f"huggingface/{llm_model}"

        # Minimal debug logs (no secrets)
        try:
            has_gemini_key = bool(os.environ.get("GEMINI_API_KEY"))
            print(f"[CrewAI] LLM model resolved: {llm_model} | GEMINI_API_KEY set: {has_gemini_key}")
        except Exception:
            pass

        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            llm=llm_model,  # Pass LiteLLM-compatible model id string
            verbose=verbose,
            max_iter=settings.MAX_ITERATIONS
        )