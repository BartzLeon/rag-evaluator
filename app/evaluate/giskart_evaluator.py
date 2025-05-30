import os
from giskard.rag import evaluate as giskart_evaluate
from giskard.rag.metrics import correctness_metric
from giskard.rag.metrics.ragas_metrics import ragas_context_precision, ragas_faithfulness, ragas_answer_relevancy, \
    ragas_context_recall
from giskard.llm.embeddings import BaseEmbedding
from giskard.llm import set_embedding_model
import time

from app.evaluate.evaluator import Evaluator
from giskard.rag import KnowledgeBase
import pandas as pd
from app.chat_models.factory import ChatModelFactory
from app.embeddings.factory import EmbeddingsFactory
from app.embeddings.giskard.factory import GiskardEmbeddingsFactory

class GiskartEvaluator(Evaluator):
    def generate_report(self):
        if self.documents is None:
            raise ValueError("Documents not provided to GiskartEvaluator")
        df = pd.DataFrame([d.page_content for d in self.documents], columns=["text"])

        ChatModelFactory.set_global_llm_model(self.judge_llm_type)

        embedding_model_instance = EmbeddingsFactory.get_embeddings("giskard/" + self.embedding_model)
        GiskardEmbeddingsFactory.set_global_embedding_model(self.embedding_model)

        try:
            knowledge_base = KnowledgeBase(
                df,
                llm_client=ChatModelFactory.get_lite_llm_model("giskard/" + self.judge_llm_type),
                embedding_model=embedding_model_instance
            )

            def answer_fn(question, history=None):
                if self.chain is None:
                    raise ValueError("Chain not initialized in GiskartEvaluator")
                return self.chain.invoke({"question": question})

            if self.testset is None:
                raise ValueError("Testset not loaded in GiskartEvaluator")

            report = giskart_evaluate(
                answer_fn,
                testset=self.testset,
                knowledge_base=knowledge_base,
                metrics=[
                    #correctness_metric,
                    #ragas_context_precision,
                    #ragas_faithfulness,
                    #ragas_answer_relevancy,
                    #ragas_context_recall,
                ],
            )

            filename = self.generate_filename()
            report.save(filename)

            scores = report.component_scores() if hasattr(report, 'component_scores') else None
            kb_score = report.knowledge_base_score if hasattr(report, 'knowledge_base_score') else None

            return filename, scores, kb_score
        finally:
            GiskardEmbeddingsFactory.reset_global_embedding_model()
            ChatModelFactory.reset_global_llm_model()

    @staticmethod
    def generate_filename():
        now = time.strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"app/data/reports/{now}/"

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        return filename
