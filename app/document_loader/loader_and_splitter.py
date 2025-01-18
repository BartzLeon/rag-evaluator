from abc import ABC, abstractmethod

from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class LoaderAndSplitter(ABC):

    def __init__(self, **kwargs) -> None:
        pass

    @abstractmethod
    def load_and_split(self):
        pass