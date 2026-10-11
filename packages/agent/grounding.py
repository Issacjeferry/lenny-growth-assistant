"""Deterministic source identity validation; semantic support still needs evaluation."""

import re

from packages.retrieval.engine import Evidence

REFUSAL = (
    "I could not find relevant evidence in the indexed Lenny's Podcast transcripts "
    "to support an answer. Try a more specific product or growth question, or index more episodes."
)


def requests_internal_instructions(content: str) -> bool:
    """Reject direct control/exfiltration requests, without blocking prompt-engineering topics."""
    return bool(
        re.search(
            r"^\s*(?:ignore|disregard|forget)\b.{0,60}\b(?:instructions|rules)\b"
            r"|\b(?:output|reveal|print|show)\s+(?:me\s+)?(?:the\s+|your\s+)?"
            r"(?:system\s+prompt|hidden\s+instructions)\b",
            content,
            re.IGNORECASE,
        )
    )


def retrieval_query(content: str, mode: str) -> str:
    if mode == "qa":
        return content
    # Remove output-format instructions from semantic search, retaining the actual topic.
    topic = re.sub(
        r"^\s*(?:write|create|generate|make|build)\b.*?\b(?:about|on|for)\s+",
        "",
        content,
        count=1,
        flags=re.IGNORECASE,
    )
    return topic.strip() or content


def cited_sources(content: str, evidence: list[Evidence]) -> list[Evidence]:
    numbers = [int(n) for n in re.findall(r"\[S(\d+)\]", content)]
    if not numbers or any(n < 1 or n > len(evidence) for n in numbers):
        return []
    return [evidence[n - 1] for n in dict.fromkeys(numbers)]


def normalize_citations(content: str) -> str:
    """Normalize explicit source IDs, without adding any references the model omitted."""
    return re.sub(
        r"\((S\d+(?:\s*,\s*S\d+)*)\)|\[(S\d+(?:\s*,\s*S\d+)+)\]",
        lambda match: " ".join(
            f"[{label.strip()}]" for label in (match.group(1) or match.group(2)).split(",")
        ),
        content,
    )


def route(content: str, selected: str) -> str:
    if selected != "qa":
        return selected
    lower = content.lower()
    if "ship 30" in lower or "ship30" in lower:
        return "ship30"
    if re.search(r"\b(create|generate|make|build|turn)\b", lower):
        if "html" in lower:
            return "html"
        if "markdown" in lower:
            return "markdown"
    return "qa"
