import pickle
from app.document_loader.loader_and_splitter import LoaderAndSplitter
import os

class CachedDocumentsLoader(LoaderAndSplitter):

    DOCUMENT_FOLDER = "app/data/documents/"

    def __init__(self, url: str = "web-scraping.pkl", **kwargs) -> None:
        super().__init__(**kwargs)
        self.url = url

    def load_and_split(self):
        with open(self.DOCUMENT_FOLDER + str(self.url) + ".pkl", "rb") as f:
            return pickle.load(f)