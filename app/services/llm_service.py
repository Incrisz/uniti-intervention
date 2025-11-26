from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.chat_models import init_chat_model
from ..config import get_settings


def prompt_llm(prompt, params):
    output_parser = JsonOutputParser()
    settings = get_settings()
    prompt = PromptTemplate.from_template(prompt).invoke(params)
    llm = init_chat_model(settings.model_name,model_provider=settings.model_provider, api_key=settings.model_api_key, temperature=0.1)
    content = llm.invoke(prompt).content
    content_parsed = output_parser.parse(content)
    content_parsed = (content_parsed["intervention_id"].lower(), content_parsed["app_id"])
    return content_parsed