# core/exception.py
"""
Custom exception helpers for the AI ChatBot project.
Provides a helpful formatting function for exception details and a wrapper exception type.
"""

from typing import Any
import traceback

def error_message_detail(error: Exception, error_detail: Any = None) -> str:
    """
    Create a formatted error message containing file, line and message.
    - error: the caught exception
    - error_detail: optional additional context
    """
    try:
        tb = error.__traceback__
        if tb is not None:
            last_tb = traceback.extract_tb(tb)[-1]
            file_name = getattr(last_tb, "filename", "<unknown>")
            line_no = getattr(last_tb, "lineno", "<unknown>")
        else:
            file_name = "<no-traceback>"
            line_no = "<no-line>"
    except Exception:
        file_name = "<error-inspecting-traceback>"
        line_no = "<error>"

    message = str(error) if error is not None else "<no-error-message>"

    if error_detail:
        return f"Error occurred in file: [{file_name}] at line: [{line_no}] Message: [{message}] Detail: [{error_detail}]"
    else:
        return f"Error occurred in file: [{file_name}] at line: [{line_no}] Message: [{message}]"

class ChatBotException(Exception):
    """
    A wrapper exception that carries a formatted error message to be used across the project.
    """

    def __init__(self, error: Exception, error_detail: Any = None):
        super().__init__(str(error))
        self.error_message = error_message_detail(error, error_detail)

    def __str__(self) -> str:
        return getattr(self, "error_message", super().__str__())