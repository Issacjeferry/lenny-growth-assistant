"""Canonical ingestion CLI; retained for existing make/Compose commands."""

from packages.retrieval.ingest import ingest, main  # noqa: F401

if __name__ == "__main__":
    main()
