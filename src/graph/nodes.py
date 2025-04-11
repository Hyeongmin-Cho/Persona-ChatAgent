from langchain_core.messages import HumanMessage, AIMessage

from src.chain.chains import (
    get_profile_messages,
    create_profiling_llm,
    create_profile_web_search_query_chain,
    create_web_search_query_chain,
    create_retrieval_evaluator,
    create_rag_chatbot_chain,
    create_response_evaluator,
    create_question_rewriter
)
from src.tools import get_web_search_tool
from src.retriever.document_retriever import (
    get_retriever,
    process_search_results,
    split_documents,
    store_documents
)


profiling_llm = create_profiling_llm()
profile_web_search_chain = create_profile_web_search_query_chain()
web_search_query_chain = create_web_search_query_chain()
retrieval_evaluator = create_retrieval_evaluator()
rag_chatbot_chain = create_rag_chatbot_chain()
response_eval_chain = create_response_evaluator()
question_rewriter = create_question_rewriter()
web_search_tool = get_web_search_tool()
doc_retriever = get_retriever()


def profiling(state):
    print("--- Profiling Node ---")
    messages = get_profile_messages(state["messages"])
    response = profiling_llm.invoke(messages)
    return {"messages": [response]}


def route_message(state):
    print("--- Routing Node ---")
    profile = state.get("profile")
    
    if profile:  # Profile 수집 완료 상태, 대화 시작
        print("\t-- Route Message To Retriever --")
        return "retriever"
    else:  # 정보 수집 노드로 라우팅
        print("\t-- Route To Profiling --")
        return "profiling"


def check_profiling(state):
    print("--- Check Profiling Node ---")
    messages = state["messages"]
    
    if isinstance(messages[-1], AIMessage) and messages[-1].tool_calls:  # Tool Call 발생했을 경우 Profile 수집 완료, "profile_web_search"로 라우팅
        print("\t-- Route Message To Profile Web Search --")
        return "profile_web_search"
    else:
        print("\t-- Profile Information Insufficient --")
        return "insufficient"


def profile_web_search(state):
    print("--- Profile Web Search Node ---")
    messages = state["messages"]
    profile = messages[-1].tool_calls[0]["args"]
    
    # 쿼리 재작성 카운터 초기화
    retries = 0
    
    # 프로필 웹 검색 시작
    profile_search_query = profile_web_search_chain.invoke({"profile": profile})
    search_results = web_search_tool.invoke(profile_search_query)

    # 수집 문서 Chunking
    docs = process_search_results(search_results)
    doc_splits = split_documents(docs)
    
    # 벡터 DB에 저장
    store_documents(doc_splits)
    
    # tool_calls 메시지 삭제
    messages.pop()
    messages.append(AIMessage(content="정보 수집 완료. 대화를 시작해주세요!"))
    
    return {"messages": messages, "profile": profile, "web_query": profile_search_query, "retries": retries}


def retriever(state):
    print("--- Retriever Node ---")
    user_message = state["messages"][-1]

    retrieved_docs = doc_retriever.invoke(user_message.content)
    state["documents"] = retrieved_docs

    return state


def evaluate_documents(state):
    print("--- Evaluate Document Node ---")
    user_message = state["messages"][-1]
    documents = state["documents"]
    profile = state["profile"]
    
    filtered_docs = []
    web_search_flag = False
    
    for doc in documents:
        evaluation = retrieval_evaluator.invoke(
            {"profile": profile, "document": doc.page_content, "message": user_message}
        )
        if evaluation.decision == "yes":
            print("\t-- Document Is Relevant To Message--")
            filtered_docs.append(doc)
        else:
            print("\t-- Document Is Not Relevant To Message--")
            web_search_flag = True
    
    state["documents"] = filtered_docs
    state["web_search_flag"] = web_search_flag
    
    return state


def decide_generation(state):
    print("--- Decide Generation ---")
    web_search_flag = state["web_search_flag"]
    
    if web_search_flag:
        print("\t-- Route To Web Search --")
        return "web_search"
    else:
        print("\t-- Route To Generate --")
        return "generate"


def web_search(state):
    print("--- Web Search Node ---")
    messages = state["messages"]
    user_message = messages[-1]
    documents = state["documents"]
    profile = state["profile"]
    web_query = state.get("web_query", [])
    
    web_search_query = web_search_query_chain.invoke({"profile": profile, "message": user_message})
    search_results = web_search_tool.invoke(web_search_query)
    
    web_query.append(web_search_query)
    state["web_query"] = web_query
    
    docs = process_search_results(search_results)
    doc_splits = split_documents(docs)
    
    try:
        store_documents(doc_splits)
        documents.extend(doc_splits)
        state["documents"] = documents
    except:
        pass
    
    return state


def generate(state):
    print("--- Generate ---")
    messages = state["messages"]
    profile = state["profile"]
    context = state["documents"]
    
    generation = rag_chatbot_chain.invoke({"profile": profile, "context": context, "messages": messages})
    state["generation"] = generation
    
    return state


def evaluate_generation(state):
    print("--- Evaluate Generation ---")
    messages = state["messages"]
    generation = state["generation"]
    documents = state["documents"]
    profile = state["profile"]
    retries = state["retries"]
    
    retry_flag = False
    if retries >= 3:  # max retry 도달한 경우 바로 답변(무한루프 방지)
        print("\t-- Reached The Maximum Number Of Retries. --")
        messages.append(AIMessage(content=generation))
        state["messages"] = messages
        state["retry_flag"] = retry_flag
        state["retries"] = 0
        return state
    else:  # max retry 도달하지 않은 경우 Response 평가
        evaluation = response_eval_chain.invoke(
            {"profile": profile, "context": documents, "messages": messages, "response": generation}
        )
        if evaluation.decision == "yes":
            print("\t-- Response Addresses The Conversation --")
            messages.append(AIMessage(content=generation))
            state["messages"] = messages
            state["retry_flag"] = retry_flag
            state["retries"] = 0
            return state
        else:
            print("\t-- Response Does Not Address The Conversation --")
            retry_flag = True
            state["retry_flag"] = retry_flag
            state["retries"] += 1
            del state["generation"]
            return state


def decide_response(state):
    print("--- Decide To Response ---")
    retry_flag = state['retry_flag']
    
    if not retry_flag:
        print("\t-- Response --")
        return "response"
    else:
        print("\t-- Rewrite query --")
        return "rewrite_query"


def rewrite_query(state):
    print("--- Rewrite User Question ---")
    messages = state["messages"]
    user_message = messages[-1]
    
    new_user_message = question_rewriter.invoke({"question": user_message.content})
    messages[-1] = HumanMessage(content=new_user_message.content)
    state["messages"] = messages
    
    return state
