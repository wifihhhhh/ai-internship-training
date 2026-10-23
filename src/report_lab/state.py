from typing import TypedDict


class ReportState(TypedDict, total=False):
    task_id: str
    question: str

    evidence: list[dict]
    draft: dict
    review: dict

    revision: int
    status: str
    artifact_path: str

    research_model_calls: int
    search_calls: int