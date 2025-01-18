from app.evaluate.Evaluator import Evaluator
from app.evaluate.GiskartEvaluator import GiskartEvaluator
from app.evaluate.RagasEvaluator import RagasEvaluator


class EvaluatorFactory:

    _evaluators = {
        RagasEvaluator.__name__: RagasEvaluator,
        GiskartEvaluator.__name__: GiskartEvaluator,
    }

    @classmethod
    def get_model(cls, evaluator: str, **kwargs) -> Evaluator:
        creator_class = cls._evaluators.get(evaluator)
        if not creator_class:
            raise ValueError(f"Unsupported model type: {evaluator}")
        return creator_class(**kwargs)