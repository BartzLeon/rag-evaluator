import pickle
from app.document_loader.loader_and_splitter import LoaderAndSplitter
import os

class CachedDocumentsLoader(LoaderAndSplitter):

    def __init__(self, url: str = "app/data/documents/web-scraping.pkl", **kwargs) -> None:
        super().__init__(**kwargs)
        self.url = url

    def load_and_split(self):
        with open(self.url, "rb") as f:
            return pickle.load(f)