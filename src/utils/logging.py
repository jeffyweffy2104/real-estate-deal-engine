import json
import logging


def get_logger(name: str = "underwriting") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    return logger


def log_event(logger: logging.Logger, event: str, **kwargs: object) -> None:
    payload = {"event": event, **kwargs}
    logger.info(json.dumps(payload, default=str, sort_keys=True))
