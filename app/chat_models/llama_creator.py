from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_mistralai.chat_models import ChatMistralAI
import os
from langchain_openai.chat_models import ChatOpenAI

from . import config
from .base import ChatModelCreator
from .config import OPENAI_API_KEY, OPEN_AI_DEFAULT_MODEL

class LlamaChatModelCreator(ChatModelCreator):
    def __init__(self, model_name: str = OPEN_AI_DEFAULT_MODEL, temperature: float = 0.7):
        self.api_key = OPENAI_API_KEY
        self.model_name = model_name
        self.temperature = temperature

    def create_model(self) -> ChatHuggingFace:
        llm = HuggingFaceEndpoint(
            repo_id="meta-llama/Llama-3.3-70B-Instruct",
            task="text-generation",
            max_new_tokens=512,
            do_sample=False,
            repetition_penalty=1.03,
            huggingfacehub_api_token=config.HUGGINGFACE_API_KEY,
        )

        return ChatHuggingFace(llm=llm)