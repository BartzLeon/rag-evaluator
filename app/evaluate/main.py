import os
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter
from giskard.rag import evaluate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings

from app.DocumnetLoader.LoaderAndSplitter import LoaderAndSplitter
from app.promt_templates import PromptTemplateFactory
from app.testset_loader.TestsetLoader import TestSetLoader
from app.vectorestores.VectorStoreFactory import VectorStoreFactory
import time
from giskard.llm.client.litellm import LiteLLMClient
from giskard.rag import KnowledgeBase
import pandas as pd


class EvaluateMain:
    MODEL = "gpt-3.5-turbo"

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

    def evaluate(self):
        testset = self.testset_loader.load()
        documents = self.document_loader.load_and_split()

        vectorstore = self.vectorstore_factory.from_documents(documents, collection_name="default",
                                                              embedding=OpenAIEmbeddings(dimensions=3072,
                                                                                         model="text-embedding-3-large"))
        retriever = vectorstore.as_retriever()

        prompt = self.prompt_template.get_template()

        df = pd.DataFrame([d.page_content for d in documents], columns=["text"])

        knowledge_base = KnowledgeBase(
            df,
            llm_client=LiteLLMClient(model=self.MODEL)
        )

        chain = self.build_chain(self.model, prompt, retriever)

        def answer_fn(question, history=None):
            return chain.invoke({"question": question})

        report = evaluate(answer_fn, testset=testset, knowledge_base=knowledge_base)

        filename = self.generate_filename()
        report.save(filename)

        return filename, report.component_scores(), report.knowledge_base_score

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

    @staticmethod
    def generate_filename():
        now = time.strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"app/data/reports/{now}/"

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        return filename
