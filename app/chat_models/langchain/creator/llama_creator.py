from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from app.chat_models.langchain.base import LangChainChatModelCreator
from app.config.llm_config import OPENAI_API_KEY, OPEN_AI_DEFAULT_MODEL

class LlamaLangChainChatModelCreator(LangChainChatModelCreator):
    def __init__(self, model_name: str = OPEN_AI_DEFAULT_MODEL):
        self.api_key = OPENAI_API_KEY
        self.model_name = model_name

    def create_model(self) -> ChatHuggingFace:
        llm = HuggingFaceEndpoint(
            repo_id="meta-llama/Llama-3.3-70B-Instruct",
            task="text-generation",
            max_new_tokens=512,
            do_sample=False,
            repetition_penalty=1.03,
            huggingfacehub_api_token=config.HUGGINGFACE_API_KEY,
            model=self.model_name,
        )

        return ChatHuggingFace(llm=llm)