"""
Data models for the pdf2qa library.
"""

from pdf2qa.models.document import Document
from pdf2qa.models.chunk import Chunk
from pdf2qa.models.statement import Statement
from pdf2qa.models.qa_pair import QAPair

__all__ = ["Document", "Chunk", "Statement", "QAPair"]
