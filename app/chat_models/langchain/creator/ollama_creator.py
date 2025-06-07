import os
from langchain_ollama import ChatOllama

from app.chat_models.langchain.base import LangChainChatModelCreator

class OllamaLangChainChatModelCreator(LangChainChatModelCreator):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def create_model(self) -> ChatOllama:

        if self.model_name.startswith("ollama/"):
            self.model_name = self.model_name[7:]

        return ChatOllama(
            model=self.model_name,
            base_url=f"http://{os.getenv('OLLAMA_IP', '192.168.5.2')}:11434"
        )
