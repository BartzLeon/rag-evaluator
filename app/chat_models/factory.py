from langchain_core.language_models import BaseChatModel

from .llama_creator import LlamaChatModelCreator
from .mistralai_creator import MistralAIChatModelCreator
from .openai_creator import OpenAIChatModelCreator
from .zephyr_creator import ZephyrModelCreator
from .qwen_creator import QwenModelCreator


class ChatModelFactory:
    _creators = {
        "openai": OpenAIChatModelCreator,
        "mistral": MistralAIChatModelCreator,
        "llama": LlamaChatModelCreator,
        "zephyr": ZephyrModelCreator,
        "qwen": QwenModelCreator,
    }

    @classmethod
    def get_model(cls, model_type: str, **kwargs) -> BaseChatModel:
        creator_class = cls._creators.get(model_type.lower())
        if not creator_class:
            raise ValueError(f"Unsupported model type: {model_type}")
        creator = creator_class(**kwargs)
        return creator.create_model()