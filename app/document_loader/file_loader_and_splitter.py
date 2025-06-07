from langchain_community.document_loaders import TextLoader, PyPDFLoader, TextLoader, Docx2txtLoader, CSVLoader, UnstructuredEmailLoader
from langchain_community.document_loaders.excel import UnstructuredExcelLoader
from langchain_community.document_loaders.powerpoint import UnstructuredPowerPointLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.document_loader.loader_and_splitter import LoaderAndSplitter
from langchain_core.documents import Document
import os
import logging

class FileLoaderAndSplitter(LoaderAndSplitter):
    def __init__(self, file_path: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.file_path = file_path

    def load_and_split(self) -> list[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Determine file type and use appropriate loader
        file_extension = os.path.splitext(self.file_path)[1].lower()
        
        if file_extension == '.pdf':
            loader = PyPDFLoader(self.file_path)
        elif file_extension == '.txt':
            loader = TextLoader(self.file_path)
        elif file_extension == '.docx' or file_extension == '.doc':
            loader = Docx2txtLoader(self.file_path)
        elif file_extension == '.xlsx' or file_extension == '.xls':
            loader = UnstructuredExcelLoader(self.file_path)
        elif file_extension == '.csv':
            loader = CSVLoader(self.file_path)
        elif file_extension == '.eml':
            loader = UnstructuredEmailLoader(self.file_path)
        elif file_extension == '.pptx' or file_extension == '.ppt':
            loader = UnstructuredPowerPointLoader(self.file_path)
        else:
            # Default to text loader for other file types
            loader = TextLoader(self.file_path)
        
        # Add error handling for invalid/corrupt docx files
        try:
            return loader.load_and_split(text_splitter)
        except KeyError as e:
            if file_extension in ['.docx', '.doc'] and "word/document.xml" in str(e):
                logging.warning(f"Skipping invalid/corrupt docx file: {self.file_path}")
                return []
            else:
                raise 