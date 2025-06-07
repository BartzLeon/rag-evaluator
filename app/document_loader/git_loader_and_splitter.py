from langchain_community.document_loaders import GitLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.document_loader.loader_and_splitter import LoaderAndSplitter
import os


class GitLoaderAndSplitter(LoaderAndSplitter):

    def __init__(self, repo_path: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.repo_path = repo_path

    def load_and_split(self) -> list[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        # Verify the repository path exists
        if not os.path.exists(self.repo_path):
            raise ValueError(f"Repository path {self.repo_path} does not exist")

        # Load the git repository
        loader = GitLoader(
            repo_path=self.repo_path,
            branch="master",
            # Filter to only load common code files and exclude binary/generated files
            file_filter=lambda file_path: file_path.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.rb', '.go', '.php', '.html', '.css', '.md', '.txt', '.vue'))
        )

        return loader.load_and_split(text_splitter) 