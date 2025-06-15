from pandas import DataFrame
from app.evaluate.evaluator import Evaluator
from ragas import evaluate as ragas_evaluate, EvaluationDataset
import pandas as pd
from app.embeddings.factory import EmbeddingsFactory
from ragas.run_config import RunConfig
import os
import time
import json

class RagasEvaluator(Evaluator):

    def generate_report(self):
        if self.chain is None:
            raise ValueError("Chain not initialized in RagasEvaluator")
        if self.retriever is None:
            raise ValueError("Retriever not initialized in RagasEvaluator")
        if self.testset is None or not hasattr(self.testset, 'to_pandas'):
            raise ValueError("Testset not loaded or not convertible to pandas DataFrame in RagasEvaluator")
        if self.judge_llm is None:
            raise ValueError("Judge LLM not provided to RagasEvaluator")

        testset_df = self.testset.to_pandas()
        dataset_list = self.build_dataset_list(self.chain, self.retriever, testset_df)

        if not dataset_list:
            # Handle empty dataset case: Ragas might error or produce empty results.
            # It might be better to return empty/None results directly.
            return None, pd.DataFrame(), None # Or appropriate empty/error indication

        evaluation_dataset = EvaluationDataset.from_list(dataset_list)
        ragas_embeddings = EmbeddingsFactory.get_embeddings("langchain/" + self.embedding_model)

        # Configure RunConfig for rate limiting and retries
        # For OpenAI Tier 1, adjust max_workers as needed. Start with a conservative value.
        # Defaults: timeout=180, max_retries=10, max_wait=60
        # We are setting max_workers; other defaults will apply.
        # You might need to adjust max_workers based on specific OpenAI model limits and observed behavior.
        # A common Tier 1 RPM might be 60-500 depending on the model.
        # If each task takes ~1-2s, max_workers=5 means ~2.5-5 req/s, or 150-300 RPM.
        # If you have lower RPM limits (e.g., 60 RPM), set max_workers to a lower value (e.g., 1 or 2).
        run_config = RunConfig(timeout=600, log_tenacity=True, max_retries=20, max_workers=2) # Adjust this value as per your specific tier limits

        # Removed embeddings preparation and parameter
        result = ragas_evaluate(
            dataset=evaluation_dataset,
            llm=self.judge_llm,
            embeddings=ragas_embeddings,
            run_config=run_config,
            show_progress=True # Can be True for overall progress
        )
        
        scores_df = result.to_pandas() if hasattr(result, 'to_pandas') else pd.DataFrame()
        
        # Add raw_responses to the scores DataFrame
        if not scores_df.empty:
            scores_df['raw_response'] = [item.get('response_raw', '') for item in dataset_list]
        
        filename = self.generate_filename()
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Save scores_df to JSON
        if not scores_df.empty:
            scores_df.to_json(filename, orient="records", indent=4)
        else:
            # Create an empty JSON file or a file with an empty list/object
            with open(filename, 'w') as f:
                json.dump([], f) # Or json.dump({}, f) depending on desired empty state

        # Ragas typically doesn't produce a separate 'report_path' or a single 'knowledge_base_score' like Giskard.
        # We return None for report_path and knowledge_base_score, and the scores DataFrame.
        return filename, scores_df, None

    @staticmethod
    def build_dataset_list(chain, retriever, testset_df: DataFrame) -> list:
        dataset = []

        for _, testset_df_row in testset_df.iterrows():
            question = testset_df_row['question']
            reference_answer = testset_df_row.get('reference_answer') # Ensure 'reference_answer' exists
            
            relevant_docs = retriever.invoke(question)
            # Changed chain invocation to match working version
            response_text_raw = chain.invoke({"context": relevant_docs, "question": question})

            # Filter out <think>...</think> blocks from response_text
            import re

            def remove_think_blocks(text):
                # Remove all occurrences of <think>...</think> (non-greedy)
                return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

            response_text = remove_think_blocks(response_text_raw)

            # Assuming chain.invoke now directly returns the string response based on working example
            # If response_text is a dict like {'answer': '...'}, it needs extraction:
            # response_output = response_text # or response_text.get('answer', '') if it's a dict

            dataset.append(
                {
                    "user_input": question,
                    "response": response_text, # Use the direct output from chain
                    "response_raw": response_text_raw,
                    "retrieved_contexts": [rdoc.page_content for rdoc in relevant_docs],
                    "reference": reference_answer if reference_answer is not None else ""
                }
            )
        return dataset

    @staticmethod
    def generate_filename():
        now = time.strftime("%Y-%m-%d-%H-%M-%S")
        # Save the JSON file in a directory named with the timestamp
        # and the file itself can be named e.g. ragas_scores.json
        filename = f"app/data/reports/{now}/ragas_scores.json"
        # os.makedirs(os.path.dirname(filename), exist_ok=True) # Directory creation handled in generate_report
        return filename