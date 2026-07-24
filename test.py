import sys

from core.logger import logger
from core.exception import ChatBotException

try:
    result = 10 / 0

except Exception as e:
    logger.exception("Division failed.")
    raise ChatBotException(e, sys)