from langchain_core.prompts import PromptTemplate

from app.promt_templates.prompt_template_factory import PromptTemplateFactory


class SimplePromptTemplate(PromptTemplateFactory):

    @staticmethod
    def get_template():
        template = """
        Answer the question based on the context below. If you can't 
        answer the question, reply "I don't know".
        
        Context: {context}
        
        Question: {question}
        """

        return PromptTemplate.from_template(template)