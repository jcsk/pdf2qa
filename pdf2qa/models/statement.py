"""
Statement model for representing a structured statement extracted from text.
"""

import uuid
from typing import List, Optional


class Statement:
    """
    Represents a structured statement extracted from text.
    
    Attributes:
        id: Unique identifier for the statement.
        text: The text content of the statement.
        pages: List of page numbers where the statement appears.
    """
    
    def __init__(
        self,
        text: str,
        pages: List[int],
        statement_id: Optional[str] = None,
    ):
        """
        Initialize a Statement.
        
        Args:
            text: The text content of the statement.
            pages: List of page numbers where the statement appears.
            statement_id: Optional unique identifier for the statement. If not provided, a UUID will be generated.
        """
        self.id = statement_id or f"statement-{uuid.uuid4()}"
        self.text = text
        self.pages = pages
    
    def __repr__(self) -> str:
        """String representation of the Statement."""
        return f"Statement(id={self.id}, pages={self.pages}, text={self.text[:50]}...)"
    
    def to_dict(self) -> dict:
        """Convert the Statement to a dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "pages": self.pages,
        }
