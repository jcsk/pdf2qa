"""
ContentExporter for exporting content to JSON format.
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Optional, Union

from pdf2qa.models import Chunk, Statement
from pdf2qa.utils.logging import get_logger

logger = get_logger()


class ContentExporter:
    """
    Exporter for saving parsed content to JSON format.
    
    Attributes:
        output_path: Path to save the output JSON file.
    """
    
    def __init__(self, output_path: Union[str, Path]):
        """
        Initialize a ContentExporter.
        
        Args:
            output_path: Path to save the output JSON file.
        """
        self.output_path = Path(output_path) if isinstance(output_path, str) else output_path
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_path.parent, exist_ok=True)
        
        logger.info(f"Initialized ContentExporter with output path: {output_path}")
    
    def export_chunks(self, chunks: List[Chunk]) -> None:
        """
        Export chunks to JSON.
        
        Args:
            chunks: List of Chunk objects.
        """
        logger.info(f"Exporting {len(chunks)} chunks to {self.output_path}")
        
        # Convert chunks to dictionaries
        chunk_dicts = [chunk.to_dict() for chunk in chunks]
        
        # Write to JSON file
        with open(self.output_path, "w") as f:
            json.dump(chunk_dicts, f, indent=2)
        
        logger.info(f"Successfully exported chunks to {self.output_path}")
    
    def export_statements(self, statements: List[Statement]) -> None:
        """
        Export statements to JSON.
        
        Args:
            statements: List of Statement objects.
        """
        logger.info(f"Exporting {len(statements)} statements to {self.output_path}")
        
        # Convert statements to dictionaries
        statement_dicts = [statement.to_dict() for statement in statements]
        
        # Write to JSON file
        with open(self.output_path, "w") as f:
            json.dump(statement_dicts, f, indent=2)
        
        logger.info(f"Successfully exported statements to {self.output_path}")
