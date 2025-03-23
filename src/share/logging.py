import os
import logging
import datetime

from pathlib import Path
from logging import Logger
from logging import handlers
from src.util.singleton import Singleton


class Logging(metaclass=Singleton):
    def __init__(self) -> None:
        self._logger = logging.getLogger(os.environ['APP_NAME'])

        self._create_log_folder()
        self._setup_logger()

    def _create_log_folder(self):
        path = Path(os.environ['LOG_FILE_PATH'])

        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

    def _setup_logger(self) -> None:
        self._logger.setLevel(logging.INFO)

        self._logger.propagate = False

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S")
        formatter.converter = lambda *args: datetime.datetime.now(datetime.timezone.utc).timetuple()

        # TimedRotatingFileHandler for automatic log file rotation
        size_handler = handlers.RotatingFileHandler(
            f"{os.environ['LOG_FILE_PATH']}/{os.environ['APP_NAME']}.log",
            maxBytes=int(os.environ['LOG_MAX_BYTES']),
            backupCount=int(os.environ['LOG_BACKUP_COUNT']),
        )
        size_handler.setFormatter(formatter)

        if not self._logger.hasHandlers():
            self._logger.addHandler(size_handler)


    def get_logger(self) -> Logger:
        return self._logger
