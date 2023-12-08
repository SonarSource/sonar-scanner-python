import logging
from logging import Logger
from typing import Optional

class ApplicationLogger():

    _log: Optional[Logger] = None

    @classmethod
    def get_logger(cls) -> Logger:
        if not cls._log:
            cls._log = logging.getLogger("main")
            cls._setup_logger(cls._log)
        return cls._log 

    @staticmethod
    def _setup_logger(log: Logger):
        log.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.terminator = ""
        log.addHandler(handler)
