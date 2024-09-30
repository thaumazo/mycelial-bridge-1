import os

def get_llm_config():
    llm_provider = os.getenv("LLM_PROVIDER", "openai")  # Default to OpenAI if not set
    if llm_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY in .env")
        return {"provider": "openai", "api_key": api_key}
    elif llm_provider == "gpt4all":
        model_path = os.getenv("GPT4ALL_MODEL_PATH")
        if not model_path:
            raise ValueError("Missing GPT4ALL_MODEL_PATH in .env")
        return {"provider": "gpt4all", "model_path": model_path}
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")
