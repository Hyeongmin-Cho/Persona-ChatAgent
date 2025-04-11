from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.tools import get_vectorstore


def get_retriever(k: int=5):
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k":5})
    return retriever

def process_search_results(search_results):
    docs = [Document(page_content=result["content"]) for result in search_results]
    return docs

def split_documents(docs, chunk_size=550, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    doc_splits = splitter.split_documents(docs)
    return doc_splits

def store_documents(docs):
    vectorstore = get_vectorstore()
    try:
        vectorstore.add_documents(docs)
        return True
    except Exception as E:
        print("Error Storing Documents: {E}")
        return False