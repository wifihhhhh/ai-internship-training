from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from src.report_lab.researcher import research_node
from src.report_lab.reviewer import review_node
from src.report_lab.state import ReportState
from src.report_lab.writer import write_node
from src.report_lab.retry import READ_RETRY
from src.report_lab.approval import approval_node, export_node, reject_node, route_after_approval


def route_after_review(state: ReportState) -> str:
    if not state["draft"]["supported"]:
        return "stop"

    if state["review"]["passed"]:
        return "finish"

    if state.get("revision", 0) < 1:
        return "revise"

    return "stop"

def revise_node(state: ReportState) -> dict:
    return {
        "revision": state.get("revision", 0) + 1,
    }

def finish_node(state: ReportState) -> dict:
    return {"status": "ready_for_human"}

def stop_node(state: ReportState) -> dict:
    return {"status": "needs_manual_revision"}

def build_graph(checkpointer=None):
    builder = StateGraph(ReportState)

    builder.add_node(
        "research", 
        research_node,
        retry_policy=READ_RETRY,
    )
    builder.add_node(
        "write", 
        write_node,
        retry_policy=READ_RETRY,
    )
    builder.add_node(
        "review", 
        review_node,
        retry_policy=READ_RETRY,
    )
    builder.add_node("revise", revise_node)
    builder.add_node("stop", stop_node)
    builder.add_node("approve", approval_node)
    builder.add_node("export", export_node)
    builder.add_node("reject", reject_node)

    builder.add_edge(START, "research")
    builder.add_edge("research", "write")
    builder.add_edge("write", "review")

    builder.add_conditional_edges(
        "review",
        route_after_review,
        {
            "finish": "approve",
            "revise": "revise",
            "stop": "stop",
        },
    )

    builder.add_edge("revise", "write")

    builder.add_conditional_edges(
        "approve",
        route_after_approval,
        {
            "export": "export",
            "reject": "reject",
        },
    )

    builder.add_edge("stop", END)
    builder.add_edge("export", END)
    builder.add_edge("reject", END)

    return builder.compile(
        checkpointer=(
            checkpointer if checkpointer is not None else InMemorySaver()
        )
    )