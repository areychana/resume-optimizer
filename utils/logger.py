"""
Structured logging for the resume optimizer.
Logs module name, duration, token counts, and errors to a rotating file.
"""

import logging
import time
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_DIR = Path(__file__).parent.parent / "logs"
_LOG_FILE = _LOG_DIR / "optimizer.log"


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger that writes to both console and a rotating log file.

    Log file: logs/optimizer.log (max 1MB, 3 backups).
    Format: timestamp | level | module | message

    Args:
        name: Logger name, typically the module name (e.g. 'optimizer').

    Returns:
        Configured Logger instance.
    """
    _LOG_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler: INFO and above
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    # File handler: DEBUG and above, rotating
    fh = RotatingFileHandler(
        _LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger


@contextmanager
def log_call(logger: logging.Logger, operation: str):
    """
    Context manager that logs the start, duration, and success/failure
    of an operation.

    Usage:
        with log_call(logger, "optimize_resume"):
            result = do_something()

    Args:
        logger: Logger instance from get_logger().
        operation: Human-readable name of the operation being timed.
    """
    logger.info(f"Starting: {operation}")
    start = time.perf_counter()
    try:
        yield
        elapsed = time.perf_counter() - start
        logger.info(f"Completed: {operation} in {elapsed:.2f}s")
    except Exception as exc:
        elapsed = time.perf_counter() - start
        logger.error(f"Failed: {operation} after {elapsed:.2f}s ({exc})")
        raise


def log_usage(logger: logging.Logger, operation: str, usage: dict) -> None:
    """
    Log token usage and cost for a Claude API call.

    Args:
        logger: Logger instance from get_logger().
        operation: Name of the operation that made the API call.
        usage: Dict from calculate_cost() with input_tokens, output_tokens, cost_usd.
    """
    logger.info(
        f"Usage [{operation}]: "
        f"in={usage.get('input_tokens', 0)} "
        f"out={usage.get('output_tokens', 0)} "
        f"total={usage.get('total_tokens', 0)} "
        f"cost={usage.get('cost_usd', '$0.0000')}"
    )
