from config import get_logger
from typing import Dict

logger = get_logger(__name__)


class Error(Exception):
    def __init__(self, message: str, context: Dict = None) -> None:
        super().__init__(message)  # Call the base class constructor
        self.message = message
        self.context = context
        # error_log = self.create_error_log()
        # if error_log:
        #     logger.debug(error_log)
