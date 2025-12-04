from django.conf import settings
from pymongo import MongoClient
from opensearchpy import OpenSearch

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

_mongo_client = None
_opensearch_client = None
_vectorstore = None


def get_mongo_collection():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(settings.MONGODB_URI)
    db = _mongo_client[settings.MONGODB_DB_NAME]
    return db["documents"]


def get_opensearch():
    global _opensearch_client
    if _opensearch_client is None:
        _opensearch_client = OpenSearch(
            hosts=[settings.OPENSEARCH_HOST],
            http_compress=True,
            use_ssl=False,
            verify_certs=False,
        )
    return _opensearch_client


def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        client = get_opensearch()
        embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        _vectorstore = OpenSearchVectorSearch(
            opensearch_url=settings.OPENSEARCH_HOST,
            index_name=settings.OPENSEARCH_INDEX,
            embedding_function=embeddings,
            http_auth=None,
            use_ssl=False,
            verify_certs=False,
        )
        # cria índice se não existir
        if not client.indices.exists(settings.OPENSEARCH_INDEX):
            client.indices.create(settings.OPENSEARCH_INDEX)
    return _vectorstore


def ingest_text(doc_id: str, text: str):
    """
    Quebra o texto em chunks, gera embeddings e indexa no OpenSearch.
    """
    vectorstore = get_vectorstore()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )
    chunks = splitter.split_text(text)

    metadatas = [{"doc_id": doc_id} for _ in chunks]

    vectorstore.add_texts(texts=chunks, metadatas=metadatas)


def answer_question(question: str) -> dict:
    """
    Usa LangChain RetrievalQA para responder com base nos chunks no OpenSearch.
    """
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    llm = ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        temperature=0.1,
        model="gpt-4o-mini",  # ou outro que você quiser
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
    )

    result = chain.invoke({"query": question})

    answer = result["result"]
    sources = []
    for doc in result["source_documents"]:
        sources.append(
            {
                "doc_id": doc.metadata.get("doc_id"),
                "snippet": doc.page_content[:200],
            }
        )

    return {"answer": answer, "sources": sources}
