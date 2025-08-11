import logging
import os
from logging.config import dictConfig

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_JSON = os.getenv("LOG_JSON", "1") in ("1", "true", "True")

BASE_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"
JSON_FORMAT = "%(message)s"  # message will already be JSON string we construct

_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": BASE_FORMAT},
        "json": {"format": JSON_FORMAT},
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "json" if LOG_JSON else "standard",
            "level": LOG_LEVEL,
        }
    },
    "loggers": {
        "": {"handlers": ["default"], "level": LOG_LEVEL, "propagate": False},
        "access": {"handlers": ["default"], "level": LOG_LEVEL, "propagate": False},
        "security": {"handlers": ["default"], "level": LOG_LEVEL, "propagate": False},
        "ai": {"handlers": ["default"], "level": LOG_LEVEL, "propagate": False},
    },
}

def setup_logging():
    dictConfig(_config)
    logging.getLogger(__name__).debug("Logging configured", extra={"component": "logging_setup"})
