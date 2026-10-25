"""로깅 설정."""
import logging
import os
import sys
import time
from contextlib import contextmanager

_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_configured = False


def setup_logging(level: str | None = None, log_file: str | None = None):
    global _configured
    if _configured:
        return
    level = (level or os.environ.get("LOG_LEVEL") or "INFO").upper()
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(level=getattr(logging, level, logging.INFO), format=_FORMAT, handlers=handlers)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)


@contextmanager
def timed(label: str, logger: logging.Logger | None = None):
    """with timed("학습"): ... 형태로 소요 시간을 남긴다."""
    logger = logger or get_logger("timer")
    t0 = time.time()
    logger.info("%s 시작", label)
    try:
        yield
    finally:
        logger.info("%s 완료 (%.1fs)", label, time.time() - t0)
