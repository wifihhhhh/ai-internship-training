import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser

from src.langchain_lab.models import build_real_model
from src.report_lab.schemas import Brief


def call_json_role(schema, instruction: str, payload: dict):
    parser = PydanticOutputParser(pydantic_object=schema)

    model = build_real_model(
        max_retries=0,
        max_tokens=1600,
    ).bind(response_format={"type": "json_object"})

    response = model.invoke([
        SystemMessage(
            content=(
                instruction
                + "\n只输出JSON。\n"
                + parser.get_format_instructions()
            )
        ),
        HumanMessage(content=json.dumps(payload, ensure_ascii=False)),
    ])

    return parser.invoke(response)

def validate_brief(brief: Brief, evidence: list[dict]) -> None:
    by_id = {
        item["chunk_id"]: item
        for item in evidence
    }

    if not brief.supported:
        if brief.citations:
            raise ValueError("无依据简报不应附带引用")
        return

    if not brief.citations:
        raise ValueError("有依据简报必须附带引用")

    for citation in brief.citations:
        item = by_id.get(citation.chunk_id)

        if item is None:
            raise ValueError("引用了未提供的片段")

        quote = citation.quote.strip()

        if not quote or quote not in item["text"]:
            raise ValueError("引用不是来源原文")