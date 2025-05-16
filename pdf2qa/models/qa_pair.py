"""
QAPair model for representing a question-answer pair.
"""

from typing import Dict, List, Optional


class QAPair:
    """
    Represents a question-answer pair for fine-tuning.
    
    Attributes:
        prompt: The question or prompt.
        completion: The answer or completion.
        metadata: Additional metadata about the QA pair, including source information.
    """
    
    def __init__(
        self,
        prompt: str,
        completion: str,
        pages: List[int],
        source: str,
        chunk_id: str,
        additional_metadata: Optional[Dict] = None,
    ):
        """
        Initialize a QAPair.
        
        Args:
            prompt: The question or prompt.
            completion: The answer or completion.
            pages: List of page numbers where the content appears.
            source: Source document identifier.
            chunk_id: ID of the chunk this QA pair was generated from.
            additional_metadata: Any additional metadata to include.
        """
        self.prompt = prompt
        self.completion = completion
        self.metadata = {
            "pages": pages,
            "source": source,
            "chunk_id": chunk_id,
        }
        
        if additional_metadata:
            self.metadata.update(additional_metadata)
    
    def __repr__(self) -> str:
        """String representation of the QAPair."""
        return f"QAPair(prompt={self.prompt[:30]}..., completion={self.completion[:30]}..., metadata={self.metadata})"
    
    def to_dict(self) -> dict:
        """Convert the QAPair to a dictionary."""
        return {
            "prompt": self.prompt,
            "completion": self.completion,
            "metadata": self.metadata,
        }
    
    def to_openai_format(self) -> dict:
        """Convert the QAPair to OpenAI fine-tuning format."""
        return {
            "messages": [
                {"role": "user", "content": self.prompt},
                {"role": "assistant", "content": self.completion}
            ]
        }
