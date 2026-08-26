import structlog

from axiom_core.config import AxiomSettings
from axiom_core.logging import bind_execution_context, configure_logging, get_logger


def test_configure_logging_is_idempotent():
    settings = AxiomSettings(_env_file=None)
    configure_logging(settings)
    configure_logging(settings)  # must not raise or duplicate handlers

    logger = get_logger("test")
    assert logger is not None


def test_bind_execution_context_merges_into_events():
    # configure_logging is deliberately idempotent (call once at process
    # startup) so this test doesn't depend on which settings won that
    # race with other tests — it asserts on structlog's own event
    # capture, not on stdout, so it's independent of the stdlib handler
    # / renderer another test may have already configured.
    configure_logging(AxiomSettings(_env_file=None))

    structlog.contextvars.clear_contextvars()
    bind_execution_context(execution_id="exec-123", tenant_id="tenant-abc")

    logger = get_logger("test")
    # capture_logs() disables all configured processors, including
    # merge_contextvars — pass it explicitly or bound context vars never
    # reach the captured event dict.
    with structlog.testing.capture_logs(
        processors=[structlog.contextvars.merge_contextvars]
    ) as captured_events:
        logger.info("axiom.test_event")

    structlog.contextvars.clear_contextvars()

    assert len(captured_events) == 1
    event = captured_events[0]
    assert event["event"] == "axiom.test_event"
    assert event["execution_id"] == "exec-123"
    assert event["tenant_id"] == "tenant-abc"
