import logging
import sys
from pprint import pformat
from typing import Union

from loguru import logger
from loguru._defaults import LOGURU_FORMAT

from config import Config


class InterceptHandler(logging.Handler):  # pragma: no cover
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level: Union[int, str] = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            if frame.f_back:
                frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


class LogConfig:
    FORMAT = Config.get("log_format", LOGURU_FORMAT)

    @staticmethod
    def setup(suppress_handlers: bool = True) -> None:
        if suppress_handlers:  # pragma: no cover
            setattr(logging.Logger, "addHandler", lambda self, handler: None)

        logging.getLogger().handlers = [InterceptHandler()]

        level = "DEBUG" if Config.debug else "INFO"
        logger.configure(
            handlers=[{"sink": sys.stdout, "level": level,
                       "format": LogConfig.FORMAT}],
        )

        for level in ["critical", "error", "warning", "info", "debug"]:
            logger.add(
                Config.LOG_PATH / f"{level}.log",
                level=level.upper(),
                format=LogConfig.FORMAT,
                rotation="10MB",
            )


class UvicornLogConfig(LogConfig):
    @staticmethod
    def setup(suppress_handlers: bool = True) -> None:
        LogConfig.setup(suppress_handlers)
        logging.getLogger("uvicorn").handlers.clear()
        logging.getLogger().handlers.clear()
        logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]

        level = logging.DEBUG if Config.debug else logging.INFO
        logger.configure(
            handlers=[
                {
                    "sink": sys.stdout,
                    "level": level,
                    "format": UvicornLogConfig.format_record,
                },
            ],
        )

    @classmethod
    def format_record(cls, record: dict) -> str:
        format_string = cls.FORMAT

        payload = record["extra"].get("payload", None)
        if payload is not None:
            record["extra"]["payload"] = pformat(
                payload,
                indent=4,
                compact=True,
                width=88,
            )
            format_string += "\n<level>{extra[payload]}</level>"

        format_string += "{exception}\n"
        return format_string


log_config = UvicornLogConfig()