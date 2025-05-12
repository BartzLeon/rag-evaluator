from langchain_community.document_loaders import TextLoader, PyPDFLoader, TextLoader, Docx2txtLoader, CSVLoader, UnstructuredEmailLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.document_loader.loader_and_splitter import LoaderAndSplitter
import os

class FileLoaderAndSplitter(LoaderAndSplitter):
    def __init__(self, file_path: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.file_path = file_path

    def load_and_split(self):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
        
        # Determine file type and use appropriate loader
        file_extension = os.path.splitext(self.file_path)[1].lower()
        
        if file_extension == '.pdf':
            loader = PyPDFLoader(self.file_path)
        elif file_extension == '.txt':
            loader = TextLoader(self.file_path)
        elif file_extension == '.docx':
            loader = Docx2txtLoader(self.file_path)
        elif file_extension == '.csv':
            loader = CSVLoader(self.file_path)
        elif file_extension == '.eml':
            loader = UnstructuredEmailLoader(self.file_path)
        else:
            # Default to text loader for other file types
            loader = TextLoader(self.file_path)
            

        return loader.load_and_split(text_splitter) 