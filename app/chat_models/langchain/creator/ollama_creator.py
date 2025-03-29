from langchain_ollama import ChatOllama

from app.chat_models.langchain.base import LangChainChatModelCreator

class OllamaLangChainChatModelCreator(LangChainChatModelCreator):
    def __init__(self, model_name: str, temperature: float = 0.7):
        self.temperature = temperature

    def create_model(self) -> ChatOllama:
        return ChatOllama(
            model="deepseek-r1:7b",
            temperature=self.temperature,
            base_url="http://host.docker.internal:11434"
        )