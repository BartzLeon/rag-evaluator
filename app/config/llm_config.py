import os
import dotenv

# Load .env first
dotenv.load_dotenv()

# Then load .env.local which will override any values from .env
dotenv.load_dotenv(".env.local", override=True)

# OpenAI Config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPEN_AI_DEFAULT_MODEL = "gpt-4-turbo"

# HuggingFace Config
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Provider Configurations
PROVIDER_CONFIGS = {
    "ollama": {
        "api_base": "http://host.docker.internal:11434",
    },
    "openai": {
        "api_key": OPENAI_API_KEY,
    },
    "huggingface": {
        "api_key": HUGGINGFACE_API_KEY,
    }
} 