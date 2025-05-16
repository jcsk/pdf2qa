"""
QAExporter for exporting question-answer pairs to JSONL format.
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Optional, Union

from pdf2qa.models import QAPair
from pdf2qa.utils.logging import get_logger

logger = get_logger()


class QAExporter:
    """
    Exporter for saving question-answer pairs to JSONL format.
    
    Attributes:
        output_path: Path to save the output JSONL file.
    """
    
    def __init__(self, output_path: Union[str, Path]):
        """
        Initialize a QAExporter.
        
        Args:
            output_path: Path to save the output JSONL file.
        """
        self.output_path = Path(output_path) if isinstance(output_path, str) else output_path
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_path.parent, exist_ok=True)
        
        logger.info(f"Initialized QAExporter with output path: {output_path}")
    
    def export(self, qa_pairs: List[QAPair], openai_format: bool = True) -> None:
        """
        Export question-answer pairs to JSONL.
        
        Args:
            qa_pairs: List of QAPair objects.
            openai_format: Whether to use OpenAI fine-tuning format.
        """
        logger.info(f"Exporting {len(qa_pairs)} Q/A pairs to {self.output_path}")
        
        # Write to JSONL file
        with open(self.output_path, "w") as f:
            for qa_pair in qa_pairs:
                if openai_format:
                    # Use OpenAI fine-tuning format
                    data = qa_pair.to_openai_format()
                else:
                    # Use standard format
                    data = qa_pair.to_dict()
                
                f.write(json.dumps(data) + "\n")
        
        logger.info(f"Successfully exported Q/A pairs to {self.output_path}")
