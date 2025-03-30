from langchain_core.language_models import BaseChatModel
import os
import giskard.llm

from app.chat_models.langchain.creator.llama_creator import LlamaLangChainChatModelCreator
from app.chat_models.langchain.creator.ollama_creator import OllamaLangChainChatModelCreator
from app.chat_models.langchain.creator.openai_creator import OpenAILangChainChatModelCreator
from app.chat_models.lite_llm.creator.ollama_creator import GiskardOllamaLiteLLMCreator

from app.config.llm_config import PROVIDER_CONFIGS


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
        "giskard/deepseek-r1:7b": GiskardOllamaLiteLLMCreator,
        "giskard/gpt-4-turbo": GiskardOllamaLiteLLMCreator,
    }

    _provider_configs = PROVIDER_CONFIGS

    @classmethod
    def get_langchain_model(cls, model_type: str, **kwargs) -> BaseChatModel:
        creator_class = cls._creators_langchain.get(model_type.lower())
        if not creator_class:
            raise ValueError(f"Unsupported model type: {model_type}")
        creator = creator_class(model_name=model_type.lower(), **kwargs)
        return creator.create_model()

    @classmethod
    def get_lite_llm_model(cls, model_type: str, **kwargs):
        creator_class = cls._creators_lite_llm.get(model_type.lower())
        if not creator_class:
            raise ValueError(f"Unsupported model type: {model_type}")
        creator = creator_class(model_name=model_type.lower(), **kwargs)
        return creator.create_model()

    @classmethod
    def available_models(cls):
        return list(cls._creators_langchain.keys())

    @classmethod
    def set_global_llm_model(cls, model_type: str, **kwargs):
        """Set the global LLM model using Giskard's set_llm_model function.
        
        Args:
            model_type: The type of model to set (e.g., "ollama/deepseek-r1:7b")
            **kwargs: Additional parameters to pass to set_llm_model
        """
        model_provider = model_type.split('/')[0].lower()
        provider_config = cls._provider_configs.get(model_provider, {})
        
        kwargs.update(provider_config)
            
        giskard.llm.set_llm_model(model_type, **kwargs)

    @classmethod
    def reset_global_llm_model(cls):
        """Reset the global LLM model to the default model from GSK_LLM_MODEL environment variable.
        Falls back to "gpt-4o" if the environment variable is not set.
        """
        default_model = os.getenv("GSK_LLM_MODEL", "gpt-4o")
        cls.set_global_llm_model(default_model)