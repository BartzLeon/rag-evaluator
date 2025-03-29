from abc import ABC, abstractmethod
from langchain_core.language_models.chat_models import BaseChatModel

class LangChainChatModelCreator(ABC):

    @abstractmethod
    def create_model(self) -> BaseChatModel:
        """Create and return a configured Chat Model."""
        pass