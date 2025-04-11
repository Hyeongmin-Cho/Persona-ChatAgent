from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage

from src.tools import get_llm
from src.prompts import PROFILE_SYSTEM
from src.schema.structured_tools import Profile, EvalDocuments, EvalResponse
from src.chain.prompts import (
    PROFILE_WEB_SERACH_PROMPT,
    WEB_QUERY_GEN_PROMPT,
    RETRIEVAL_EVAL_PROMPT,
    RAG_PROMPT,
    RESPONSE_EVAL_PROMPT,
    REWRITE_PROMPT
)

def get_profile_messages(messages):
    return [SystemMessage(content=PROFILE_SYSTEM)] + messages


def create_profiling_llm():
    llm = get_llm(model="gpt-4o-mini")
    llm_with_tools = llm.bind_tools([Profile])
    return llm_with_tools


def create_profile_web_search_query_chain():
    llm = get_llm(model="gpt-4o-mini")
    chain = PROFILE_WEB_SERACH_PROMPT | llm | StrOutputParser()
    return chain


def create_web_search_query_chain():
    llm = get_llm(model="gpt-4o-mini")
    chain = WEB_QUERY_GEN_PROMPT | llm | StrOutputParser()
    return chain
    
    
def create_retrieval_evaluator():
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    retrieval_llm_evaluator = llm.with_structured_output(EvalDocuments)
    chain = RETRIEVAL_EVAL_PROMPT | retrieval_llm_evaluator
    return chain


def create_rag_chatbot_chain():
    llm = get_llm(model="gpt-4o-mini")
    chain = RAG_PROMPT | llm | StrOutputParser()
    return chain


def create_response_evaluator():
    llm = get_llm(model="gpt-4o-mini", temperature=0)
    response_llm_evaluator = llm.with_structured_output(EvalResponse)
    chain = RESPONSE_EVAL_PROMPT | response_llm_evaluator
    return chain


def create_question_rewriter():
    llm = get_llm(model="gpt-4o-mini")
    chain = REWRITE_PROMPT | llm
    return chain