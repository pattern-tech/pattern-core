import os
import logging

from pathlib import Path
from logging import Logger
from logging import handlers
from src.util.singleton import Singleton


class Logging(metaclass=Singleton):
    def __init__(self) -> None:
        self._logger = logging.getLogger(os.environ['app_name'])

        self._create_log_folder()
        self._setup_logger()

    def _create_log_folder(self):
        path = Path(os.environ['log_file_path'])

        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

    def _setup_logger(self) -> None:
        self._logger.setLevel(logging.INFO)

        self._logger.propagate = False

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] - %(message)s")

        # TimedRotatingFileHandler for automatic log file rotation
        size_handler = handlers.RotatingFileHandler(
            f"{os.environ['log_file_path']}/{os.environ['app_name']}.log",
            maxBytes=int(os.environ['log_max_bytes']),
            backupCount=int(os.environ['log_backup_count']),
        )
        size_handler.setFormatter(formatter)

        if not self._logger.hasHandlers():
            self._logger.addHandler(size_handler)


    def get_logger(self) -> Logger:
        return self._logger
