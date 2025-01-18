from abc import ABC, abstractmethod


class PromptTemplateFactory(ABC):

    @staticmethod
    @abstractmethod
    def get_template():
        pass