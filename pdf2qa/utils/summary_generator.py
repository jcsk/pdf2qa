"""
Summary generator for creating comprehensive processing reports.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from pdf2qa.models import Chunk, QAPair, Statement
from pdf2qa.utils.cost_tracker import cost_tracker
from pdf2qa.utils.logging import get_logger

logger = get_logger()


class ProcessingSummary:
    """Comprehensive summary of a pdf2qa processing run."""
    
    def __init__(self, job_id: str, input_path: Union[str, Path]):
        """Initialize processing summary."""
        self.job_id = job_id
        self.input_path = Path(input_path)
        self.start_time = datetime.now()
        self.end_time = None
        
        # Document metrics
        self.document_size_bytes = 0
        self.estimated_pages = 0
        
        # Processing metrics
        self.chunks_created = 0
        self.statements_extracted = 0
        self.qa_pairs_generated = 0
        
        # Performance metrics
        self.processing_time_seconds = 0.0
        self.parsing_time_seconds = 0.0
        self.extraction_time_seconds = 0.0
        self.qa_generation_time_seconds = 0.0
        
        # Cost metrics
        self.total_cost_usd = 0.0
        self.llamaparse_cost_usd = 0.0
        self.openai_cost_usd = 0.0
        self.openai_tokens_used = 0
        
        # Output files
        self.output_files = {}
        
        # Stage timers
        self._stage_start_time = None
        
        # Get initial document metrics
        self._analyze_input_document()
    
    def _analyze_input_document(self):
        """Analyze the input document for basic metrics."""
        try:
            if self.input_path.exists():
                self.document_size_bytes = self.input_path.stat().st_size
                logger.info(f"Document size: {self.document_size_bytes:,} bytes")
        except Exception as e:
            logger.warning(f"Could not analyze input document: {e}")
    
    def start_stage(self, stage_name: str):
        """Start timing a processing stage."""
        self._stage_start_time = datetime.now()
        logger.debug(f"Started stage: {stage_name}")
    
    def end_stage(self, stage_name: str) -> float:
        """End timing a processing stage and return duration."""
        if self._stage_start_time is None:
            return 0.0
        
        duration = (datetime.now() - self._stage_start_time).total_seconds()
        logger.debug(f"Completed stage: {stage_name} in {duration:.2f}s")
        return duration
    
    def record_parsing_results(self, chunks: List[Chunk], duration: float):
        """Record parsing stage results."""
        self.chunks_created = len(chunks)
        self.parsing_time_seconds = duration
        
        # Estimate pages from chunks
        if chunks:
            all_pages = set()
            for chunk in chunks:
                all_pages.update(chunk.pages)
            self.estimated_pages = len(all_pages)
        
        logger.info(f"Parsing: {self.chunks_created} chunks, {self.estimated_pages} pages, {duration:.2f}s")
    
    def record_extraction_results(self, statements: List[Statement], duration: float):
        """Record extraction stage results."""
        self.statements_extracted = len(statements)
        self.extraction_time_seconds = duration
        logger.info(f"Extraction: {self.statements_extracted} statements, {duration:.2f}s")
    
    def record_qa_results(self, qa_pairs: List[QAPair], duration: float):
        """Record QA generation stage results."""
        self.qa_pairs_generated = len(qa_pairs)
        self.qa_generation_time_seconds = duration
        logger.info(f"QA Generation: {self.qa_pairs_generated} pairs, {duration:.2f}s")
    
    def record_output_file(self, file_type: str, file_path: Union[str, Path]):
        """Record an output file."""
        file_path = Path(file_path)
        self.output_files[file_type] = {
            "path": str(file_path),
            "size_bytes": file_path.stat().st_size if file_path.exists() else 0,
            "created_at": datetime.now().isoformat()
        }
    
    def finalize(self):
        """Finalize the summary with cost data and total time."""
        self.end_time = datetime.now()
        self.processing_time_seconds = (self.end_time - self.start_time).total_seconds()
        
        # Get cost data from cost tracker
        cost_summary = cost_tracker.get_summary()
        
        # Filter costs for this job
        job_costs = cost_summary.get("by_job", {}).get(self.job_id, {"cost": 0.0})
        self.total_cost_usd = job_costs.get("cost", 0.0)
        
        # Break down by service
        for call in cost_tracker.calls:
            if call.job_id == self.job_id:
                if call.service == "llamaparse":
                    self.llamaparse_cost_usd += call.cost_usd
                elif call.service == "openai":
                    self.openai_cost_usd += call.cost_usd
                    self.openai_tokens_used += call.total_tokens
        
        logger.info(f"Processing completed: {self.processing_time_seconds:.2f}s, ${self.total_cost_usd:.4f}")
    
    def to_dict(self) -> Dict:
        """Convert summary to dictionary."""
        return {
            "job_id": self.job_id,
            "input_document": {
                "path": str(self.input_path),
                "size_bytes": self.document_size_bytes,
                "estimated_pages": self.estimated_pages
            },
            "processing_metrics": {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "total_time_seconds": self.processing_time_seconds,
                "parsing_time_seconds": self.parsing_time_seconds,
                "extraction_time_seconds": self.extraction_time_seconds,
                "qa_generation_time_seconds": self.qa_generation_time_seconds
            },
            "output_metrics": {
                "chunks_created": self.chunks_created,
                "statements_extracted": self.statements_extracted,
                "qa_pairs_generated": self.qa_pairs_generated,
                "statements_per_chunk": round(self.statements_extracted / max(self.chunks_created, 1), 2),
                "qa_pairs_per_statement": round(self.qa_pairs_generated / max(self.statements_extracted, 1), 2)
            },
            "cost_metrics": {
                "total_cost_usd": round(self.total_cost_usd, 4),
                "llamaparse_cost_usd": round(self.llamaparse_cost_usd, 4),
                "openai_cost_usd": round(self.openai_cost_usd, 4),
                "openai_tokens_used": self.openai_tokens_used,
                "cost_per_page": round(self.total_cost_usd / max(self.estimated_pages, 1), 4),
                "cost_per_qa_pair": round(self.total_cost_usd / max(self.qa_pairs_generated, 1), 4)
            },
            "performance_metrics": {
                "pages_per_second": round(self.estimated_pages / max(self.processing_time_seconds, 1), 2),
                "chunks_per_second": round(self.chunks_created / max(self.parsing_time_seconds, 1), 2),
                "statements_per_second": round(self.statements_extracted / max(self.extraction_time_seconds, 1), 2),
                "qa_pairs_per_second": round(self.qa_pairs_generated / max(self.qa_generation_time_seconds, 1), 2)
            },
            "output_files": self.output_files
        }
    
    def save_to_file(self, output_path: Union[str, Path]):
        """Save summary to JSON file."""
        output_path = Path(output_path)
        
        try:
            with open(output_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            logger.info(f"Processing summary saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save summary to {output_path}: {e}")
    
    def print_summary(self):
        """Print a formatted summary to console."""
        print("\n" + "="*80)
        print("📊 PROCESSING SUMMARY")
        print("="*80)
        print(f"🆔 Job ID: {self.job_id}")
        print(f"📄 Document: {self.input_path.name}")
        print(f"📏 Size: {self.document_size_bytes:,} bytes ({self.estimated_pages} pages)")
        
        print(f"\n⏱️  Processing Time:")
        print(f"   Total: {self.processing_time_seconds:.2f}s")
        print(f"   Parsing: {self.parsing_time_seconds:.2f}s")
        print(f"   Extraction: {self.extraction_time_seconds:.2f}s")
        print(f"   QA Generation: {self.qa_generation_time_seconds:.2f}s")
        
        print(f"\n📊 Output Metrics:")
        print(f"   Chunks: {self.chunks_created}")
        print(f"   Statements: {self.statements_extracted}")
        print(f"   Q/A Pairs: {self.qa_pairs_generated}")
        
        print(f"\n💰 Cost Breakdown:")
        print(f"   Total: ${self.total_cost_usd:.4f}")
        print(f"   LlamaParse: ${self.llamaparse_cost_usd:.4f}")
        print(f"   OpenAI: ${self.openai_cost_usd:.4f} ({self.openai_tokens_used:,} tokens)")
        
        if self.estimated_pages > 0:
            print(f"   Cost per page: ${self.total_cost_usd / self.estimated_pages:.4f}")
        if self.qa_pairs_generated > 0:
            print(f"   Cost per Q/A pair: ${self.total_cost_usd / self.qa_pairs_generated:.4f}")
        
        print(f"\n🚀 Performance:")
        if self.processing_time_seconds > 0:
            print(f"   Pages/second: {self.estimated_pages / self.processing_time_seconds:.2f}")
            print(f"   Q/A pairs/second: {self.qa_pairs_generated / self.processing_time_seconds:.2f}")
        
        print(f"\n📁 Output Files:")
        for file_type, info in self.output_files.items():
            size_kb = info["size_bytes"] / 1024
            print(f"   {file_type}: {info['path']} ({size_kb:.1f} KB)")
        
        print("="*80)


# Global summary instance
current_summary: Optional[ProcessingSummary] = None


def start_processing_summary(job_id: str, input_path: Union[str, Path]) -> ProcessingSummary:
    """Start a new processing summary."""
    global current_summary
    current_summary = ProcessingSummary(job_id, input_path)
    return current_summary


def get_current_summary() -> Optional[ProcessingSummary]:
    """Get the current processing summary."""
    return current_summary
