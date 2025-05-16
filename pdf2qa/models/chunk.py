"""
Chunk model for representing a chunk of text from a document.
"""

import uuid
from typing import List, Optional


class Chunk:
    """
    Represents a chunk of text from a document.
    
    Attributes:
        id: Unique identifier for the chunk.
        text: The text content of the chunk.
        pages: List of page numbers where the chunk appears.
        section: Optional section name or title.
    """
    
    def __init__(
        self,
        text: str,
        pages: List[int],
        section: Optional[str] = None,
        chunk_id: Optional[str] = None,
    ):
        """
        Initialize a Chunk.
        
        Args:
            text: The text content of the chunk.
            pages: List of page numbers where the chunk appears.
            section: Optional section name or title.
            chunk_id: Optional unique identifier for the chunk. If not provided, a UUID will be generated.
        """
        self.id = chunk_id or f"chunk-{uuid.uuid4()}"
        self.text = text
        self.pages = pages
        self.section = section
    
    def __repr__(self) -> str:
        """String representation of the Chunk."""
        return f"Chunk(id={self.id}, pages={self.pages}, section={self.section}, text={self.text[:50]}...)"
    
    def to_dict(self) -> dict:
        """Convert the Chunk to a dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "pages": self.pages,
            "section": self.section,
        }
