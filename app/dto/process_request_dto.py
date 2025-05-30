from pydantic import BaseModel, Field

class ProcessRequestDTO(BaseModel):
    llm_to_be_evaluated_type: str = Field(..., description="Type of the chat model to be evaluated (e.g., openai/gpt-4-turbo)")
    judge_llm_type: str = Field(..., description="Type of the chat model to be the judge (e.g., openai/gpt-4-turbo)")
    testset: int = Field(..., description="ID of the testset to use")