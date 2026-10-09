"""Deterministic source identity validation; semantic support still needs evaluation."""

import re

from packages.retrieval.engine import Evidence

REFUSAL = (
    "I could not find relevant evidence in the indexed Lenny's Podcast transcripts "
    "to support an answer. Try a more specific product or growth question, or index more episodes."
)


def cited_sources(content: str, evidence: list[Evidence]) -> list[Evidence]:
    numbers = [int(n) for n in re.findall(r"\[S(\d+)\]", content)]
    if not numbers or any(n < 1 or n > len(evidence) for n in numbers):
        return []
    return [evidence[n - 1] for n in dict.fromkeys(numbers)]


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
