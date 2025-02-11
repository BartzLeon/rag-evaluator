import os
import openai
from giskard.llm.client.openai import OpenAIClient
from giskard.rag import evaluate as giskart_evaluate

from app.chat_models import config
from app.evaluate.evaluator import Evaluator
import time
from giskard.llm.client.litellm import LiteLLMClient
from giskard.rag import KnowledgeBase
import pandas as pd


class GiskartEvaluator(Evaluator):
    MODEL = "gpt-4-turbo"

    def generate_report(self):
        df = pd.DataFrame([d.page_content for d in self.documents], columns=["text"])
        knowledge_base = KnowledgeBase(
            df,
            llm_client=LiteLLMClient(model=self.MODEL)
        )

        def answer_fn(question, history=None):
            return self.chain.invoke({"question": question})

        report = giskart_evaluate(
            answer_fn,
            llm_client=OpenAIClient(self.MODEL, openai.OpenAI(api_key=config.OPENAI_API_KEY)),
            testset=self.testset,
            knowledge_base=knowledge_base
        )

        filename = self.generate_filename()
        report.save(filename)

        return filename, report.component_scores(), report.knowledge_base_score


    @staticmethod
    def generate_filename():
        now = time.strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"app/data/reports/{now}/"

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        return filename
