"""
Custom exception module for the AI Chatbot project.

Provides a reusable custom exception that captures the
file name, line number, and original error message.
"""

import sys
from typing import Any


def error_message_detail(error: Exception, error_detail: Any) -> str:
    """
    Create a detailed error message with file name and line number.

    Args:
        error (Exception): Original exception.
        error_detail (Any): sys module.

    Returns:
        str: Formatted error message.
    """
    _, _, exc_tb = error_detail.exc_info()

    if exc_tb is None:
        return str(error)

    file_name = exc_tb.tb_frame.f_code.co_filename

    return (
        f"Error occurred in file: [{file_name}] "
        f"at line: [{exc_tb.tb_lineno}] "
        f"Message: [{str(error)}]"
    )


class ChatBotException(Exception):
    """
    Custom exception class for the AI Chatbot project.
    """

    def __init__(self, error: Exception, error_detail: Any):
        super().__init__(str(error))
        self.error_message = error_message_detail(
            error=error,
            error_detail=error_detail,
        )

    def __str__(self) -> str:
        return self.error_message