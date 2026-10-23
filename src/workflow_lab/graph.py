import json
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver

from src.langchain_lab.models import build_real_model
from src.rag_lab.retrieval import retrieve
from src.rag_lab.service import answer_from_hits
from src.workflow_lab.state import RagState


def initialize_node(state: RagState) -> dict:
    question = state["question"]
    history = state.get("history", [])

    if history:
        response = build_real_model().invoke([
            SystemMessage(
                content=(
                    "根据历史，把当前追问改写成一个独立问题。"
                    "保持原意，不回答问题，不补造事实。"
                    "只输出改写后的问题。"
                )
            ),
            HumanMessage(
                content=(
                    f"历史：{json.dumps(history, ensure_ascii=False)}\n"
                    f"当前问题：{question}"
                )
            ),
        ])

        question = str(response.content).strip() or question
    
    return {
        "question": question,
        "search_query": question,
        "attempts": 0,
        "hits": [],
        "result": {},
    }

def retrieve_node(state: RagState) -> dict:
    hits = retrieve(state["search_query"], k=3)

    return {
        "hits": [
            {
                "text": document.page_content,
                "metadata": document.metadata,
                "distance": distance,
            } for document, distance in hits
        ]
    }

def answer_node(state: RagState) -> dict:
    hits = [
        (
            Document(
                page_content=item["text"],
                metadata=item["metadata"],
            ),
            item["distance"]
        ) for item in state["hits"]
    ]

    result = answer_from_hits(state["question"], hits)

    return {"result": result.model_dump()}

def build_graph():
    builder = StateGraph(RagState)

    builder.add_node("initialize", initialize_node)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("answer", answer_node)
    builder.add_node("rewrite", rewrite_node)
    builder.add_node("finalize", finalize_node)

    builder.add_edge(START, "initialize")
    builder.add_edge("initialize", "retrieve")
    builder.add_edge("retrieve", "answer")
    # builder.add_edge("answer", END)

    builder.add_conditional_edges(
        "answer",
        route_after_answer,
        {
            "finish": "finalize",
            "rewrite": "rewrite",
        },
    )
    builder.add_edge("rewrite", "retrieve")
    builder.add_edge("finalize", END)

    return builder.compile(checkpointer=InMemorySaver())

def rewrite_node(state: RagState) -> dict:
    response = build_real_model().invoke([
        SystemMessage(
            content=(
                "你负责改写知识库检索问题。"
                "保持原问题含义，用清楚的主题词重新表达。"
                "只输出一条检索问题，不回答问题，不补造事实。"
            )
        ),
        HumanMessage(
            content=(
                f"原问题：{state['question']}\n"
                f"上一条检索问题：{state['search_query']}"
            )
        ),
    ])

    query = str(response.content).strip()

    if not query:
        query = state["question"]

    return {
        "search_query": query,
        "attempts": state["attempts"] + 1,
    }

def route_after_answer(state: RagState) -> str:
    if state["result"]["supported"]:
        return "finish"

    if state["attempts"] >= 1:
        return "finish"

    return "rewrite"

def finalize_node(state: RagState) -> dict:
    history = state.get("history", []) + [{
        "question": state["question"],
        "answer": state["result"]["answer"],
    }]

    # 本地练习保留最近 4 轮，限制上下文大小。
    return {"history": history[-4:]}