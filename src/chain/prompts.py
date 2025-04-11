from langchain_core.prompts import ChatPromptTemplate
from src.prompts import (
    PROFILE_SEARCH_SYSTEM,
    PROFILE_SEARCH_USER,
    RETRIEVAL_EVAL_SYSTEM,
    RETRIEVAL_EVAL_USER,
    WEB_QUERY_GEN_SYSTEM,
    WEB_QUERY_GEN_USER,
    RAG_SYSTEM,
    RAG_USER,
    RESPONSE_EVAL_SYSTEM,
    RESPONSE_EVAL_USER,
    REWRITE_SYSTEM,
    REWRITE_USER
)


def gen_prompt(system_message, user_message):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("user", user_message)
        ]
    )
    return prompt


PROFILE_WEB_SERACH_PROMPT = gen_prompt(PROFILE_SEARCH_SYSTEM, PROFILE_SEARCH_USER)

WEB_QUERY_GEN_PROMPT = gen_prompt(WEB_QUERY_GEN_SYSTEM, WEB_QUERY_GEN_USER)

RETRIEVAL_EVAL_PROMPT = gen_prompt(RETRIEVAL_EVAL_SYSTEM, RETRIEVAL_EVAL_USER)

RAG_PROMPT = gen_prompt(RAG_SYSTEM, RAG_USER)

RESPONSE_EVAL_PROMPT = gen_prompt(RESPONSE_EVAL_SYSTEM, RESPONSE_EVAL_USER)

REWRITE_PROMPT = gen_prompt(REWRITE_SYSTEM, REWRITE_USER)
