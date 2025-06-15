from abc import abstractmethod, ABC
from operator import itemgetter
from typing import List, Any, Optional

from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.vectorstores import VectorStore

from app.promt_templates.prompt_template_factory import PromptTemplateFactory
from app.testset_loader.testset_loader import TestSetLoader


class Evaluator(ABC):

    def __init__(
            self,
            testset_loader: TestSetLoader,
            prompt_template: PromptTemplateFactory,
            model_to_be_evaluated: BaseChatModel,
            judge_llm: BaseChatModel,
            judge_llm_type: str,
            documents: List[Document],
            vectorstore: VectorStore,
            embedding_model: str,
            rating_id: int
    ):
        self.testset_loader = testset_loader
        self.model_to_be_evaluated = model_to_be_evaluated
        self.judge_llm = judge_llm
        self.judge_llm_type = judge_llm_type
        self.prompt_template = prompt_template
        self.documents = documents
        self.vectorstore = vectorstore
        self.embedding_model = embedding_model
        self.rating_id = rating_id
        self.chain: Optional[Any] = None
        self.prompt: Optional[Any] = None
        self.retriever: Optional[Any] = None
        self.testset: Optional[Any] = None


    def evaluate(self):
        self.testset = self.testset_loader.load()
        self.retriever = self.vectorstore.as_retriever()
        self.prompt = self.prompt_template.get_template()
        self.chain = self.build_chain(self.model_to_be_evaluated, self.prompt, self.retriever)

        return self.generate_report()

    @abstractmethod
    def generate_report(self):
        pass

    @staticmethod
    def build_chain(chat_model: BaseChatModel, prompt: Any, retriever: Any):
        chain = (
                RunnablePassthrough.assign(
                    context=itemgetter("question") | retriever | (lambda docs: "\n".join([doc.page_content for doc in docs]))
                )
                | prompt
                | chat_model
                | StrOutputParser()
        )

        return chain
