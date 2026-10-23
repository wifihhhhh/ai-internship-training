from langgraph.types import interrupt

from src.report_lab.export import render_report, report_digest, save_once
from src.report_lab.helpers import validate_brief
from src.report_lab.schemas import ApprovalDecision, Brief


def approval_node(state: dict) -> dict:
    text = render_report(state)
    digest = report_digest(text)

    decision = ApprovalDecision.model_validate(
        interrupt({
            "message": "请检查报告，确认是否导出",
            "title": state["draft"]["title"],
            "preview": text,
            "digest": digest,
        })
    )

    if decision.digest != digest:
        raise ValueError("批准内容与当前报告不一致")

    return {
        "status": (
            "approved" if decision.approved else "rejected"
        )
    }

def route_after_approval(state: dict) -> str:
    return (
        "export" if state["status"] == "approved" else "reject"
    )

def export_node(state: dict) -> dict:
    if state["status"] != "approved":
        raise ValueError("未经人工批准，禁止导出")

    validate_brief(
        Brief.model_validate(state["draft"]),
        state["evidence"],
    )

    path = save_once(
        state["task_id"],
        render_report(state)
    )

    return {
        "artifact_path": str(path),
        "status": "exported",
    }

def reject_node(state: dict) -> dict:
    return {"status": "rejected"}