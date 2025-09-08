from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OLLAMA_HOST: str = "http://localhost:11434"   # Local Ollama endpoint
    MODEL_NAME: str = "llama3.2"

settings = Settings()

