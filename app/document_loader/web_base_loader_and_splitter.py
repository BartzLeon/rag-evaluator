from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.document_loader.loader_and_splitter import LoaderAndSplitter


class WebBaseLoaderAndSplitter(LoaderAndSplitter):

    #def __init__(self, url: str = "https://www.ml.school/", **kwargs) -> None:
    def __init__(self, url: str = "https://web-scraping.dev/products", **kwargs) -> None:
        super().__init__(**kwargs)
        self.url = url

    def load_and_split(self):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)

        loader = WebBaseLoader(self.url)
        return loader.load_and_split(text_splitter)