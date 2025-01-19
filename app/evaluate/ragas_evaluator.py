from pandas import DataFrame
from app.evaluate.evaluator import Evaluator
from ragas import evaluate as ragas_evaluate, EvaluationDataset


class RagasEvaluator(Evaluator):
    MODEL = "gpt-3.5-turbo"


    def generate_report(self):
        dataset = self.build_dataset(self.chain, self.retriever, self.testset.to_pandas())

        evaluation_dataset = EvaluationDataset.from_list(dataset)

        result = ragas_evaluate(
            llm=None,
            dataset=evaluation_dataset,
            #metrics=[LLMContextRecall(), Faithfulness(), FactualCorrectness()],
        )

        return None, result.to_pandas(), None

    @staticmethod
    def build_dataset(chain, retriever, testset_df: DataFrame):
        dataset = []

        for _, testset_df_row in testset_df.iterrows():
            relevant_docs = retriever.invoke(testset_df_row['question'])
            response = chain.invoke({"context": relevant_docs, "question": testset_df_row['question']})
            dataset.append(
                {
                    "user_input": testset_df_row['question'],
                    "retrieved_contexts": [rdoc.page_content for rdoc in relevant_docs],
                    "response": response,
                    "reference": testset_df_row['reference_answer'],
                }
            )
        return dataset