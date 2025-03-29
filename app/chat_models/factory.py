from langchain_core.language_models import BaseChatModel

from app.chat_models.langchain.creator.llama_creator import LlamaLangChainChatModelCreator
from app.chat_models.langchain.creator.ollama_creator import OllamaLangChainChatModelCreator
from app.chat_models.langchain.creator.openai_creator import OpenAILangChainChatModelCreator


class ChatModelFactory:
    _creators_langchain = {
        "openai/gpt-4": OpenAILangChainChatModelCreator,
        "openai/gpt-4-turbo": OpenAILangChainChatModelCreator,
        "openai/gpt-4-o": OpenAILangChainChatModelCreator,
        "openai/gpt4-o-mini": OpenAILangChainChatModelCreator,
        "meta-llama/Llama-3.3-70B-Instruct": LlamaLangChainChatModelCreator,
        "deepseek": OllamaLangChainChatModelCreator,
    }

    _creators_lite_llm = {
        "lite_llm": OllamaLangChainChatModelCreator,
    }

    @classmethod
    def get_langchain_model(cls, model_type: str, **kwargs) -> BaseChatModel:
        creator_class = cls._creators_langchain.get(model_type.lower())
        if not creator_class:
            raise ValueError(f"Unsupported model type: {model_type}")
        creator = creator_class(model_name=model_type.lower(), **kwargs)
        return creator.create_model()

    @classmethod
    def get_lite_llm_model(cls, model_type: str, **kwargs) -> BaseChatModel:
        creator_class = cls._creators_lite_llm.get(model_type.lower())
        if not creator_class:
            raise ValueError(f"Unsupported model type: {model_type}")
        creator = creator_class(model_name=model_type.lower(), **kwargs)
        return creator.create_model()

    @classmethod
    def available_models(cls):
        return list(cls._creators_langchain.keys())