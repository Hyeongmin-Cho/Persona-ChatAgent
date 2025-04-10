from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.vectorstores import Chroma


def get_llm(model: str="gpt-4o-mini", temperature: float=0.8):
    llm = ChatOpenAI(model=model, temperature=temperature)
    return llm


def get_vectorstore(name: str="default"):
    vectorstore = Chroma(collection_name=name,embedding_function=OpenAIEmbeddings())
    return vectorstore


def get_web_search_tool(max_results=3):
    web_search_tool = TavilySearchResults(max_results=max_results)
    return web_search_tool