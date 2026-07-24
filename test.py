import sys

from core.logger import logger
from core.exception import ChatBotException

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

print("LangChain Core working")
try:
    result = 10 / 0

except Exception as e:
    logger.exception("Division failed.")
    raise ChatBotException(e, sys)

