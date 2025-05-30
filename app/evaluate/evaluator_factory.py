from app.evaluate.evaluator import Evaluator
from app.evaluate.giskart_evaluator import GiskartEvaluator
from app.evaluate.ragas_evaluator import RagasEvaluator
from langchain_core.language_models import BaseChatModel
from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document
from typing import List
from app.testset_loader.testset_loader import TestSetLoader
from app.promt_templates.prompt_template_factory import PromptTemplateFactory


class EvaluatorFactory:

    _evaluators = {
        RagasEvaluator.__name__: RagasEvaluator,
        GiskartEvaluator.__name__: GiskartEvaluator,
    }

    @classmethod
    def get_model(cls, 
                  evaluator: str, 
                  testset_loader: TestSetLoader,
                  prompt_template: PromptTemplateFactory,
                  model_to_be_evaluated: BaseChatModel,
                  judge_llm: BaseChatModel,
                  judge_llm_type: str,
                  documents: List[Document],
                  vectorstore: VectorStore,
                  embedding_model: str,
                  **kwargs) -> Evaluator:
        creator_class = cls._evaluators.get(evaluator)
        if not creator_class:
            raise ValueError(f"Unsupported evaluator type: {evaluator}")
        return creator_class(
            testset_loader=testset_loader,
            prompt_template=prompt_template,
            model_to_be_evaluated=model_to_be_evaluated,
            judge_llm=judge_llm,
            judge_llm_type=judge_llm_type,
            documents=documents,
            vectorstore=vectorstore,
            embedding_model=embedding_model,
            **kwargs
        )