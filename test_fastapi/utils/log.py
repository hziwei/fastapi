import sys
from pathlib import Path
from typing import TYPE_CHECKING

import loguru

if TYPE_CHECKING:
    from loguru import Logger

logger: "Logger" = loguru.logger


default_format: str = (
    "<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</g> ["
    "level:<lvl>{level}</lvl> - "
    "thread:{thread} - "
    "name:<c>{name}</c>:<c>{module}</c>:<c>{function}</c>:<c>{line}</c> - "
    # "task_id:<e>{extra[task_id]}</e> - "
    "trace_id:<e>{extra[trace_id]}</e>] "
    "{message}"
)


def init_logger(log_sink_stdout, log_sink_file, log_file):
    if not Path(log_file).parent.exists():
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    if log_sink_stdout:
        logger_id = logger.add(
            sys.stdout,
            level=0,
            colorize=True,
            backtrace=True,
            diagnose=True,
            filter=None,
            format=default_format,
            catch=True,
            enqueue=True
        )
        if log_sink_file:
            logger_id = logger.add(
                log_file,
                level=0,
                retention=10,
                colorize=False,
                # backtrace=True,
                diagnose=False,
                filter=None,
                format=default_format,
            )
    else:
        logger_id = logger.add(
            log_file,
            level=0,
            retention=10,
            colorize=False,
            # backtrace=True,
            diagnose=False,
            filter=None,
            format=default_format,
        )

    # Default values
    logger.configure(extra={"trace_id": ""})

    return logger_id