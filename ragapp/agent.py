from django.conf import settings

from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType

from .rag_core import get_vectorstore


def _search_knowledge(query: str) -> str:
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    docs = retriever.invoke(query)
    joined = "\n\n".join([d.page_content for d in docs])
    return joined


def run_agent(goal: str) -> str:
    """
    Agente bem simples: recebe um objetivo (goal),
    pode chamar a tool de busca e devolve um texto final.
    """
    llm = ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        temperature=0.2,
        model="gpt-4o-mini",
    )

    tools = [
        Tool(
            name="search_knowledge",
            func=_search_knowledge,
            description="Use esta ferramenta para buscar informações relevantes nos documentos indexados.",
        )
    ]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False,
    )

    # O goal é o prompt de alto nível
    result = agent.run(goal)
    return result
