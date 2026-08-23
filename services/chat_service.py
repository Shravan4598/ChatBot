"""
services/chat_service.py

Production Chat Service.

Responsibilities
----------------
• Manage conversations
• Manage LangGraph
• Manage checkpoints
• Manage uploaded documents
• Invoke workflow
• Stream responses
"""

from __future__ import annotations

from typing import Any, Dict, Generator
import uuid

from langchain_core.messages import HumanMessage

from core.exception import ChatBotException
from core.logger import logging

from graph.workflow import ChatbotWorkflow

from services.document_service import DocumentService
from services.conversation_service import ConversationService
from services.checkpoint_service import CheckpointService


class ChatService:
    """
    Production Chat Service.
    """

    def __init__(self) -> None:

        try:

            logging.info("Initializing ChatService...")

            self.graph = ChatbotWorkflow().get_graph()

            self.conversations = ConversationService()

            logging.info("ChatService initialized.")

        except Exception as e:
            raise ChatBotException(e)

    # ==========================================================
    # Thread
    # ==========================================================

    @staticmethod
    def create_thread_id() -> str:
        """
        Generate new thread id.
        """
        return str(uuid.uuid4())

    # ==========================================================
    # Conversation
    # ==========================================================

    def create_conversation(self, title: str = "New Chat") -> str:
        """
        Create a new conversation.
        """
        return self.conversations.create(title)

    # ==========================================================
    # Build State
    # ==========================================================

    def _build_state(self, user_input: str, thread_id: str) -> Dict[str, Any]:
        document_service = DocumentService(thread_id)

        return {
            "messages": [HumanMessage(content=user_input)],
            "user_input": user_input,
            "thread_id": thread_id,
            "selected_tool": None,
            "tool_input": None,
            "tool_output": None,
            "uploaded_files": document_service.list_files(),
            "active_document": None,
            "youtube_url": None,
            "rag_available": document_service.rag_available(),
            "metadata": {},
            "final_response": "",
        }

    # ==========================================================
    # Configuration
    # ==========================================================

    @staticmethod
    def _config(thread_id: str) -> dict:
        return {"configurable": {"thread_id": thread_id}}

    # ==========================================================
    # Chat
    # ==========================================================

    def chat(self, user_input: str, thread_id: str) -> str:
        """
        Synchronous chat invocation that returns the final response.
        """
        try:
            if not self.conversations.exists(thread_id):
                self.conversations.create(title=user_input[:40])

            state = self._build_state(user_input, thread_id)

            result = self.graph.invoke(state, config=self._config(thread_id))

            answer = result.get("final_response", "")

            self.conversations.update_message(thread_id, answer)

            logging.info("Chat completed successfully.")

            return answer

        except Exception as e:
            raise ChatBotException(e)

    # ==========================================================
    # Streaming
    # ==========================================================

    def stream(self, user_input: str, thread_id: str) -> Generator[dict, None, None]:
        """
        Stream events from the workflow.

        Yields dict events of shape:
          - {"type": "tool", "tool": "<tool_name>"}
          - {"type": "text", "content": "<partial-or-final-text>"}

        If the underlying graph produces no streamed text events, this method will
        fall back to calling the synchronous `chat()` method and yield one text event
        so the UI always receives a response.
        """
        try:
            if not self.conversations.exists(thread_id):
                self.conversations.create(title=user_input[:40])

            state = self._build_state(user_input, thread_id)

            yielded_text = False

            # Iterate events from the compiled graph's stream
            for event in self.graph.stream(state, config=self._config(thread_id)):
                # Defensive: ignore non-dict events unless they're raw strings
                if isinstance(event, str):
                    # Some chains may yield plain strings; treat as text chunk
                    yielded_text = True
                    self.conversations.update_message(thread_id, event)
                    yield {"type": "text", "content": event}
                    continue

                if not isinstance(event, dict):
                    continue

                # Normalize tool selection if present on event
                if event.get("selected_tool"):
                    yield {"type": "tool", "tool": event["selected_tool"]}

                # If a node emitted a final_response in the event, yield it
                if event.get("final_response"):
                    final_text = event["final_response"]
                    yielded_text = True
                    self.conversations.update_message(thread_id, final_text)
                    yield {"type": "text", "content": final_text}

            # Fallback: if streaming produced nothing, call synchronous chat() and yield that result
            if not yielded_text:
                logging.warning("No streaming text events received; falling back to synchronous chat() call.")
                try:
                    final = self.chat(user_input, thread_id)
                    # Yield the final response as a single text event
                    yield {"type": "text", "content": final}
                except Exception as e:
                    logging.exception("Fallback synchronous chat() failed: %s", e)
                    raise ChatBotException(e)

        except Exception as e:
            raise ChatBotException(e)

    # ==========================================================
    # Documents
    # ==========================================================

    def upload_document(self, thread_id: str, uploaded_file) -> dict:
        service = DocumentService(thread_id)
        return service.save_file(uploaded_file)

    def list_documents(self, thread_id: str) -> list[dict]:
        return DocumentService(thread_id).list_files()

    def clear_documents(self, thread_id: str) -> None:
        DocumentService(thread_id).clear()

    # ==========================================================
    # Conversations
    # ==========================================================

    def list_conversations(self) -> list[dict]:
        return self.conversations.list_conversations()

    def get_conversation(self, thread_id: str):
        return self.conversations.get(thread_id)

    def rename_conversation(self, thread_id: str, title: str) -> None:
        self.conversations.rename(thread_id, title)

    def delete_conversation(self, thread_id: str) -> None:
        self.conversations.delete(thread_id)

    # ==========================================================
    # History
    # ==========================================================

    def list_threads(self) -> list[str]:
        return CheckpointService.list_threads()

    def thread_exists(self, thread_id: str) -> bool:
        return CheckpointService.thread_exists(thread_id)

    # ==========================================================
    # Statistics
    # ==========================================================

    def statistics(self) -> dict:
        return {"threads": len(self.list_threads()), "conversations": self.conversations.count()}

    # ==========================================================
    # Reset
    # ==========================================================

    def reset_chat(self, thread_id: str) -> None:
        self.clear_documents(thread_id)
        logging.info("Chat reset: %s", thread_id)

    # ==========================================================
    # Health
    # ==========================================================

    def ping(self) -> bool:
        return self.graph is not None and CheckpointService.ping()