"""
Document model for representing a document to be processed.
"""

from pathlib import Path
from typing import Dict, Optional, Union


class Document:
    """
    Represents a document to be processed.
    
    Attributes:
        path: Path to the document file.
        metadata: Additional metadata about the document.
    """
    
    def __init__(self, path: Union[str, Path], metadata: Optional[Dict] = None):
        """
        Initialize a Document.
        
        Args:
            path: Path to the document file.
            metadata: Additional metadata about the document.
        """
        self.path = Path(path) if isinstance(path, str) else path
        self.metadata = metadata or {}
        
    def __repr__(self) -> str:
        """String representation of the Document."""
        return f"Document(path={self.path}, metadata={self.metadata})"
    
    @property
    def file_type(self) -> str:
        """Get the file type of the document."""
        return self.path.suffix.lower().lstrip(".")
    
    @property
    def exists(self) -> bool:
        """Check if the document file exists."""
        return self.path.exists()
