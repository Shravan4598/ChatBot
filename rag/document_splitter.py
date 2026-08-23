# rag/document_splitter.py
"""
rag/document_splitter.py

Production-ready document splitter.

Responsibilities
----------------
- Split LangChain Documents into chunks
- Preserve metadata
- Configurable chunk size and overlap
- Support all document types

This module uses RecursiveCharacterTextSplitter from langchain if available.
If not present, it falls back to a lightweight, local implementation that
implements the same methods used by the rest of the codebase.
"""

from __future__ import annotations

from typing import List, Iterable
from copy import deepcopy

from langchain_core.documents import Document

from config.config import settings
from core.exception import ChatBotException
from core.logger import logging

# Try to import the splitter from common LangChain locations
RecursiveCharacterTextSplitter = None
_import_error = None
try:
    from langchain_core.text_splitter import RecursiveCharacterTextSplitter  # type: ignore
except Exception as e1:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore
    except Exception as e2:
        RecursiveCharacterTextSplitter = None
        _import_error = (e1, e2)


# Fallback implementation
class LocalRecursiveCharacterTextSplitter:
    """
    Lightweight fallback splitter that mimics the public API used by this project.

    Behavior:
    - Attempts to split using separators in order.
    - If chunks are still larger than chunk_size, falls back to simple window-chunking.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] | None = None,
        length_function=len,
        is_separator_regex: bool = False,
    ):
        self.chunk_size = int(chunk_size)
        self.chunk_overlap = int(chunk_overlap)
        self.separators = separators or ["\n\n", "\n", ". ", "? ", "! ", ";", ",", " ", ""]
        self.length_function = length_function

    def _chunk_by_separator(self, text: str, sep: str) -> List[str]:
        if sep == "":
            # final fallback; don't split
            return [text]
        parts = text.split(sep)
        # reattach separator to keep readability (except at the end)
        for i in range(len(parts) - 1):
            parts[i] = parts[i].rstrip() + sep + " "
        return [p.strip() for p in parts if p.strip()]

    def _recurse_split(self, text: str, separators: List[str]) -> List[str]:
        # If text is small enough, return it.
        if self.length_function(text) <= self.chunk_size or not separators:
            return [text.strip()] if text.strip() else []

        sep = separators[0]
        pieces = self._chunk_by_separator(text, sep)

        # If splitting by this separator produced pieces that are all small enough,
        # keep them; otherwise recurse into each piece with the next separators.
        result: List[str] = []
        for piece in pieces:
            if self.length_function(piece) <= self.chunk_size:
                result.append(piece)
            else:
                # recurse with remaining separators
                result.extend(self._recurse_split(piece, separators[1:]))
        return result

    def split_text(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []

        text = text.strip()
        chunks = self._recurse_split(text, self.separators)

        # Final step: ensure all chunks obey chunk_size by slicing if necessary
        final_chunks: List[str] = []
        for chunk in chunks:
            if self.length_function(chunk) <= self.chunk_size:
                final_chunks.append(chunk)
            else:
                # Slide window chunking
                start = 0
                text_len = self.length_function(chunk)
                while start < text_len:
                    end = start + self.chunk_size
                    final_chunks.append(chunk[start:end])
                    start = end - self.chunk_overlap
                    if start < 0:
                        start = 0
        return final_chunks

    def split_documents(self, documents: Iterable[Document]) -> List[Document]:
        output: List[Document] = []
        for doc in documents:
            text = doc.page_content or ""
            chunks = self.split_text(text)
            for idx, c in enumerate(chunks):
                new_meta = deepcopy(doc.metadata or {})
                # Add page and chunk metadata similar to LangChain splitter
                new_meta.update({"page": new_meta.get("page"), "chunk_index": idx + 1})
                output.append(Document(page_content=c, metadata=new_meta))
        return output


# DocumentSplitter wrapper used in the rest of the codebase
class DocumentSplitter:
    """
    Production document splitter shim that hides whether we use LangChain's
    implementation or the local fallback.
    """

    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None) -> None:
        try:
            self.chunk_size = chunk_size or settings.CHUNK_SIZE
            self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

            if RecursiveCharacterTextSplitter is not None:
                # Use the imported class
                self.splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                    separators=[
                        "\n\n",
                        "\n",
                        ". ",
                        "? ",
                        "! ",
                        ";",
                        ",",
                        " ",
                        "",
                    ],
                    length_function=len,
                    is_separator_regex=False,
                )
                logging.info("Using LangChain RecursiveCharacterTextSplitter.")
            else:
                # Fallback
                self.splitter = LocalRecursiveCharacterTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                    separators=[
                        "\n\n",
                        "\n",
                        ". ",
                        "? ",
                        "! ",
                        ";",
                        ",",
                        " ",
                        "",
                    ],
                    length_function=len,
                    is_separator_regex=False,
                )
                logging.info("Using LocalRecursiveCharacterTextSplitter fallback.")
        except Exception as e:
            raise ChatBotException(e)

    # ==========================================================
    # Split Documents
    # ==========================================================

    def split_documents(self, documents: List[Document]) -> List[Document]:
        try:
            if not documents:
                raise ValueError("No documents supplied.")
            logging.info("Splitting %d document(s)...", len(documents))
            chunks = self.splitter.split_documents(documents)
            # Add chunk metadata
            for index, chunk in enumerate(chunks):
                if chunk.metadata is None:
                    chunk.metadata = {}
                chunk.metadata.update({"chunk_id": index + 1, "chunk_size": len(chunk.page_content)})
            logging.info("Generated %d chunks.", len(chunks))
            return chunks
        except Exception as e:
            raise ChatBotException(e)

    # ==========================================================
    # Split Text
    # ==========================================================

    def split_text(self, text: str) -> List[str]:
        try:
            if not text or not text.strip():
                return []
            chunks = self.splitter.split_text(text)
            logging.info("Generated %d text chunks.", len(chunks))
            return chunks
        except Exception as e:
            raise ChatBotException(e)

    # ==========================================================
    # Configuration
    # ==========================================================

    @property
    def configuration(self) -> dict:
        return {"chunk_size": self.chunk_size, "chunk_overlap": self.chunk_overlap}