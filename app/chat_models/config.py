import os
import dotenv
dotenv.load_dotenv()

# OpenAI Config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPEN_AI_DEFAULT_MODEL = "gpt-3.5-turbo"

# HuggingFace Config
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")