import logging
import sys
from typing import Any, MutableMapping

import structlog


def _add_required_fields(
    logger: Any, method_name: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    event_dict.setdefault("request_id", None)
    event_dict.setdefault("session_id", None)
    event_dict.setdefault("model", None)
    event_dict.setdefault("latency_ms", None)
    event_dict.setdefault("error_code", None)
    if "message" not in event_dict:
        event_dict["message"] = str(event_dict.get("event", ""))
    return event_dict


def configure_logging(level: str = "INFO") -> None:
    log_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
        force=True,
    )

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
        _add_required_fields,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=list(shared_processors) + [structlog.processors.JSONRenderer()],  # type: ignore[arg-type]
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(*args: Any, **kwargs: Any) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(*args, **kwargs)
