from abc import abstractmethod, ABC
from operator import itemgetter

from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings

from app.document_loader.loader_and_splitter import LoaderAndSplitter
from app.embeddings.factory import EmbeddingsFactory
from app.promt_templates.prompt_template_factory import PromptTemplateFactory
from app.testset_loader.testset_loader import TestSetLoader
from app.vectorestores.vector_store_factory import VectorStoreFactory


class Evaluator(ABC):

    def __init__(
            self,
            testset_loader: TestSetLoader,
            prompt_template: PromptTemplateFactory,
            model: BaseChatModel,
            document_loader: LoaderAndSplitter,
            vectorstore_factory: VectorStoreFactory,
    ):
        self.document_loader = document_loader
        self.testset_loader = testset_loader
        self.model = model
        self.prompt_template = prompt_template
        self.vectorstore_factory = vectorstore_factory

        self.chain = None
        self.prompt = None
        self.retriever = None
        self.vectorstore = None
        self.documents = None
        self.testset = None


    def evaluate(self):
        self.testset = self.testset_loader.load()
        self.documents = self.document_loader.load_and_split()

        #embeddings = EmbeddingsFactory.get_embeddings("ollama/nomic-embed-text:latest")
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.vectorstore = self.vectorstore_factory.from_documents(
            self.documents,
            collection_name="default",
            embedding=embeddings,
        )
        self.retriever = self.vectorstore.as_retriever()
        self.prompt = self.prompt_template.get_template()
        self.chain = self.build_chain(self.model, self.prompt, self.retriever)

        return self.generate_report()

    @abstractmethod
    def generate_report(self):
        pass

    @staticmethod
    def build_chain(chat_model, prompt, retriever):
        chain = (
                RunnablePassthrough.assign(
                    context=itemgetter("question") | retriever | (lambda docs: "\n".join([doc.page_content for doc in docs]))
                )
                | prompt
                | chat_model
                | StrOutputParser()
        )

        return chain
