"""Parse source metadata and retain exact offsets into the original transcript."""

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import yaml

TIMESTAMP = re.compile(r"\((?:(\d{1,2}):)?(\d{1,2}):(\d{2})\)")


@dataclass
class Passage:
    content: str
    start: int
    end: int
    timestamp: int | None


@dataclass
class Transcript:
    title: str
    guest: str
    url: str
    digest: str
    passages: list[Passage]


def parse_transcript(path: Path, max_chars: int = 2400, overlap: int = 300) -> Transcript:
    if max_chars < 100 or not 0 <= overlap < max_chars:
        raise ValueError("Invalid chunk window")
    raw = path.read_text(encoding="utf-8-sig")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", raw, re.DOTALL)
    if not match:
        raise ValueError(f"Missing YAML frontmatter: {path.name}")
    metadata = yaml.safe_load(match.group(1))
    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be an object")
    title, guest, url = (
        str(metadata.get(k, "")).strip() for k in ("title", "guest", "youtube_url")
    )
    parsed = urlparse(url)
    if not title or not guest or parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("Title, guest and HTTPS source URL are required")
    if parsed.username or parsed.password:
        raise ValueError("Source URLs must not contain credentials")
    # A named guest in the title must agree with frontmatter. Conflicting source
    # metadata cannot safely produce a title/URL citation. Leave the raw file intact.
    named_guest = re.search(r"\|\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})(?:\s*\(|$)", title)
    if named_guest:
        title_names = set(re.findall(r"[a-z]+", named_guest.group(1).lower()))
        guest_names = set(re.findall(r"[a-z]+", guest.lower()))
        if not title_names.intersection(guest_names):
            raise ValueError("Guest conflicts with the named guest in the episode title")
    start = match.end()
    passages = []
    stamps = [
        (m.start(), sum(int(n or 0) * factor for n, factor in zip(m.groups(), (3600, 60, 1))))
        for m in TIMESTAMP.finditer(raw)
    ]
    while start < len(raw):
        end = min(start + max_chars, len(raw))
        if end < len(raw):
            boundary = raw.rfind("\n", start + max_chars // 2, end)
            if boundary < 0:
                boundary = raw.rfind(" ", start + max_chars // 2, end)
            if boundary > start:
                end = boundary
        text = raw[start:end]
        if text.strip():
            before = [seconds for offset, seconds in stamps if offset <= start]
            within = [seconds for offset, seconds in stamps if start <= offset < end]
            timestamp = before[-1] if before else (within[0] if within else None)
            passages.append(Passage(text, start, end, timestamp))
        if end == len(raw):
            break
        start = max(start + 1, end - overlap)
    return Transcript(title, guest, url, hashlib.sha256(raw.encode()).hexdigest(), passages)
