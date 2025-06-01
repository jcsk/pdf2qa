"""
LlamaParser for parsing documents using LlamaParse.
"""

import os
from typing import List, Optional

from llama_cloud_services import LlamaParse

from pdf2qa.models import Chunk, Document
from pdf2qa.utils.logging import get_logger
from pdf2qa.utils.cost_tracker import cost_tracker

logger = get_logger()


class LlamaParser:
    """
    Parser that uses LlamaParse to extract text from documents.

    Attributes:
        api_key: LlamaParse API key.
        language: Language of the document.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        language: str = "en",
        chunk_size: int = 1500,
        chunk_overlap: int = 200,
    ):
        """
        Initialize a LlamaParser.

        Args:
            api_key: LlamaParse API key. If not provided, will try to get from environment.
            language: Language of the document.
        """
        self.api_key = api_key or os.environ.get("LLAMA_CLOUD_API_KEY")
        if not self.api_key:
            raise ValueError(
                "LlamaParse API key not provided. "
                "Either pass it directly or set the LLAMA_CLOUD_API_KEY environment variable."
            )

        self.language = language
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.parser = LlamaParse(
            api_key=self.api_key,
            verbose=True,
            language=self.language,
        )

        logger.info(f"Initialized LlamaParser with language: {language}")

    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        Split text into chunks with specified size and overlap.

        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks

        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # If this is not the last chunk, try to find a good break point
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                search_start = max(start + chunk_size - 100, start)
                sentence_end = -1

                for i in range(end - 1, search_start - 1, -1):
                    if text[i] in '.!?':
                        sentence_end = i + 1
                        break

                # If we found a sentence ending, use it
                if sentence_end > start:
                    end = sentence_end
                # Otherwise, look for word boundaries
                else:
                    while end > start and text[end] not in ' \t\n':
                        end -= 1
                    if end == start:  # No word boundary found, use original end
                        end = start + chunk_size

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start position with overlap
            start = end - chunk_overlap
            if start <= 0:
                start = end

        return chunks

    def parse(self, document: Document, job_id: Optional[str] = None) -> List[Chunk]:
        """
        Parse a document into chunks.

        Args:
            document: Document to parse.

        Returns:
            List of Chunk objects.

        Raises:
            FileNotFoundError: If the document file does not exist.
            ValueError: If the document file type is not supported.
        """
        if not document.exists:
            raise FileNotFoundError(f"Document file not found: {document.path}")

        supported_types = ["pdf", "docx", "doc", "txt"]
        if document.file_type not in supported_types:
            raise ValueError(
                f"Unsupported document type: {document.file_type}. "
                f"Supported types: {', '.join(supported_types)}"
            )

        logger.info(f"Parsing document: {document.path}")

        # Parse the document using LlamaParse
        try:
            # Parse the document
            result = self.parser.parse(str(document.path))

            # Get markdown documents (chunking parameters are not supported by LlamaParse API)
            markdown_documents = result.get_markdown_documents(
                split_by_page=True,
            )
            logger.info(f"Successfully parsed document into {len(markdown_documents)} page-based chunks")

            # Convert to our Chunk model and apply custom chunking
            chunks = []
            for i, doc in enumerate(markdown_documents):
                # Extract page numbers from metadata if available
                pages = []
                if hasattr(doc, "metadata") and "page_label" in doc.metadata:
                    try:
                        pages = [int(doc.metadata["page_label"])]
                    except (ValueError, TypeError):
                        pages = [i + 1]  # Default to chunk index + 1 if page label is not a valid integer
                elif hasattr(doc, "metadata") and "page" in doc.metadata:
                    try:
                        pages = [int(doc.metadata["page"])]
                    except (ValueError, TypeError):
                        pages = [i + 1]  # Default to chunk index + 1 if page is not a valid integer
                else:
                    pages = [i + 1]  # Default to chunk index + 1

                # Extract section from metadata if available
                section = None
                if hasattr(doc, "metadata") and "section" in doc.metadata:
                    section = doc.metadata["section"]

                # Apply custom chunking if the text is larger than chunk_size
                text_chunks = self._chunk_text(doc.text, self.chunk_size, self.chunk_overlap)

                for chunk_text in text_chunks:
                    chunk = Chunk(
                        text=chunk_text,
                        pages=pages,
                        section=section,
                    )
                    chunks.append(chunk)

            logger.info(f"Applied custom chunking, resulting in {len(chunks)} final chunks")

            # Track LlamaParse cost (estimate pages from chunks)
            estimated_pages = len(markdown_documents)
            cost_tracker.track_llamaparse_call(
                pages=estimated_pages,
                job_id=job_id,
                metadata={
                    "document_path": str(document.path),
                    "chunks_created": len(chunks),
                    "chunk_size": self.chunk_size,
                    "chunk_overlap": self.chunk_overlap
                }
            )

            return chunks

        except Exception as e:
            logger.error(f"Error parsing document: {e}")
            raise
