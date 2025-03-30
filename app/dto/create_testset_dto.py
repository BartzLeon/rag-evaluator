from typing import List
from pydantic import BaseModel, Field

class CreateTestsetDTO(BaseModel):
    name: str = Field(..., description="Name of the document")
    document: int = Field(..., description="Document ID")
    model_type: str = Field(..., description="Model type eg. gpt3.5-turbo")
    embedding_model: str = Field(..., description="Embedding model eg. openai/text-embedding-3-large")
    num_questions: int = Field(60, description="Number of questions to generate")
    agent_description: str = Field("A chatbot answering questions about the Machine Learning School Website", description="Description of the agent")