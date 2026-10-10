"""Quarantine inconsistent metadata without deleting raw files or stored history."""

import argparse
import json
from pathlib import Path

from sqlalchemy import select

from packages.retrieval.transcripts import parse_transcript
from packages.shared.db import SessionLocal
from packages.shared.db_models import Episode


def audit(root: Path) -> dict:
    files = {f"{p.parent.name}/transcript.md": p for p in root.rglob("transcript.md")}
    result: dict = {"eligible": 0, "quarantined": []}
    with SessionLocal() as db:
        seen = set()
        episodes = sorted(db.scalars(select(Episode)), key=lambda e: len(e.source_path))
        for episode in episodes:
            key = "/".join(Path(episode.source_path).parts[-2:])
            path = files.get(key)
            try:
                if key in seen:
                    raise ValueError("Duplicate source path alias; canonical record retained")
                if path is None:
                    raise ValueError("Source file is missing")
                transcript = parse_transcript(path)
                if transcript.digest != episode.content_hash:
                    raise ValueError("Source changed; re-ingestion required")
                episode.source_valid = True
                seen.add(key)
                result["eligible"] += 1
            except ValueError as exc:
                episode.source_valid = False
                result["quarantined"].append(
                    {"source_path": episode.source_path, "reason": str(exc)}
                )
        db.commit()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, default=Path("data/raw"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/source-audit.json"))
    args = parser.parse_args()
    result = audit(args.path)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
