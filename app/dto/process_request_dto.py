from pydantic import BaseModel, Field

class ProcessRequestDTO(BaseModel):
    model_type: str = Field(..., description="Type of the chat model (e.g., openai)")
    dataset: int = Field(..., description="ID of the dataset to use")