import os
import openai
from giskard.llm.client.openai import OpenAIClient
from giskard.rag import evaluate as giskart_evaluate
from giskard.rag.metrics import correctness_metric
from giskard.rag.metrics.ragas_metrics import ragas_context_precision, ragas_faithfulness, ragas_answer_relevancy, \
    ragas_context_recall

from app.config.llm_config import OPEN_AI_DEFAULT_MODEL, OPENAI_API_KEY
from app.evaluate.evaluator import Evaluator
import time
from giskard.rag import KnowledgeBase
import pandas as pd
from app.chat_models.factory import ChatModelFactory


class GiskartEvaluator(Evaluator):
    MODEL = "gpt-4-turbo"

    def generate_report(self):
        df = pd.DataFrame([d.page_content for d in self.documents], columns=["text"])

        #ChatModelFactory.set_global_llm_model("ollama/nomic-embed-text")
        ChatModelFactory.set_global_llm_model("openai/gpt-4-turbo")

        knowledge_base = KnowledgeBase(
            df,
            llm_client=OpenAIClient(self.MODEL, openai.OpenAI(api_key=OPENAI_API_KEY)),
        )

        def answer_fn(question, history=None):
            return self.chain.invoke({"question": question})

        report = giskart_evaluate(
            answer_fn,
            testset=self.testset,
            knowledge_base=knowledge_base,
            #metrics=[
            #    correctness_metric,
            #    ragas_context_precision,
            #    ragas_faithfulness,
            #    ragas_answer_relevancy,
            #    ragas_context_recall,
            #],
        )

        filename = self.generate_filename()
        report.save(filename)

        ChatModelFactory.reset_global_llm_model()

        return filename, report.component_scores(), report.knowledge_base_score


    @staticmethod
    def generate_filename():
        now = time.strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"app/data/reports/{now}/"

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        return filename
