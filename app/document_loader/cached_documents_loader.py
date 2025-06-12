import pickle
from pathlib import Path
from app.document_loader.loader_and_splitter import LoaderAndSplitter

class CachedDocumentsLoader(LoaderAndSplitter):

    @property
    def DOCUMENT_FOLDER(self) -> Path:
        # Get the path to the current file
        current_file = Path(__file__).resolve()
        # Get the app directory (parent of document_loader)
        app_dir = current_file.parent.parent
        # Return the documents directory
        return app_dir / "data" / "documents"

    def __init__(self, url: str = "web-scraping.pkl", **kwargs) -> None:
        super().__init__(**kwargs)
        self.url = url

    def load_and_split(self):
        file_path = self.DOCUMENT_FOLDER / f"{self.url}.pkl"
        with open(file_path, "rb") as f:
            return pickle.load(f)