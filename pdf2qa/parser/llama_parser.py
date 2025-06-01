"""
LlamaParser for parsing documents using LlamaParse.
"""

import os
from typing import List, Optional

from llama_cloud_services import LlamaParse

from pdf2qa.models import Chunk, Document
from pdf2qa.utils.logging import get_logger

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

    def parse(self, document: Document) -> List[Chunk]:
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

            # Get markdown documents with custom chunking parameters
            markdown_documents = result.get_markdown_documents(
                split_by_page=True,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
            logger.info(f"Successfully parsed document into {len(markdown_documents)} chunks")

            # Convert to our Chunk model
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

                chunk = Chunk(
                    text=doc.text,
                    pages=pages,
                    section=section,
                )
                chunks.append(chunk)

            return chunks

        except Exception as e:
            logger.error(f"Error parsing document: {e}")
            raise
