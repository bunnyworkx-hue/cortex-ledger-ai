import logging
import sys

import structlog

from axiom_core.config import AxiomSettings

_configured = False


def configure_logging(settings: AxiomSettings) -> None:
    """Configure stdlib logging + structlog once per process. Safe to call
    more than once — subsequent calls are no-ops.
    """
    global _configured
    if _configured:
        return

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer()
        if settings.log_format == "json"
        else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[*shared_processors, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(settings.log_level.upper())

    _configured = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)


def bind_execution_context(**fields: object) -> None:
    """Bind fields (``execution_id``, ``tenant_id``, ``agent_id``, ...)
    onto every subsequent log line emitted on this async task/thread,
    until ``structlog.contextvars.clear_contextvars()`` is called.

    This is the foundation Milestone 17 (Observability) builds execution
    tracing on top of — introduced here so every later log line already
    carries context instead of retrofitting it in later.
    """
    structlog.contextvars.bind_contextvars(**fields)


def clear_execution_context() -> None:
    """Pair with bind_execution_context() — clears bound fields so they
    don't leak into unrelated log lines on a reused task/thread (e.g. a
    connection-pool worker).
    """
    structlog.contextvars.clear_contextvars()
