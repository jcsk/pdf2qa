"""
Pipeline for orchestrating the pdf2qa workflow.
"""

import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

from pdf2qa.exporters import ContentExporter, QAExporter
from pdf2qa.extractor import LlamaExtractor
from pdf2qa.models import Chunk, Document, QAPair, Statement
from pdf2qa.parser import LlamaParser
from pdf2qa.qa_generator import QAGenerator
from pdf2qa.utils.config import get_default_config, load_config
from pdf2qa.utils.logging import get_logger, setup_logging
from pdf2qa.utils.cost_tracker import cost_tracker
from pdf2qa.utils.summary_generator import start_processing_summary

logger = get_logger()


class Pipeline:
    """
    Pipeline for orchestrating the pdf2qa workflow.

    Attributes:
        config: Configuration dictionary.
        parser: LlamaParser instance.
        extractor: LlamaExtractor instance.
        qa_generator: QAGenerator instance.
        content_exporter: ContentExporter instance.
        qa_exporter: QAExporter instance.
    """

    def __init__(self, config: Dict):
        """
        Initialize a Pipeline.

        Args:
            config: Configuration dictionary.
        """
        self.config = config

        # Initialize components
        self._init_parser()
        self._init_extractor()
        self._init_qa_generator()
        self._init_exporters()

        logger.info("Pipeline initialized")

    @classmethod
    def from_config(cls, config_path: Union[str, Path]) -> "Pipeline":
        """
        Create a Pipeline from a configuration file.

        Args:
            config_path: Path to the configuration file.

        Returns:
            Pipeline instance.
        """
        config = load_config(config_path)
        return cls(config)

    @classmethod
    def from_defaults(cls) -> "Pipeline":
        """
        Create a Pipeline with default configuration.

        Returns:
            Pipeline instance.
        """
        config = get_default_config()
        return cls(config)

    def _init_parser(self) -> None:
        """Initialize the parser component."""
        parser_config = self.config.get("parser", {})
        self.parser = LlamaParser(
            api_key=parser_config.get("api_key"),
            language=parser_config.get("language", "en"),
            chunk_size=parser_config.get("chunk_size", 1500),
            chunk_overlap=parser_config.get("chunk_overlap", 200),
        )

    def _init_extractor(self) -> None:
        """Initialize the extractor component."""
        extractor_config = self.config.get("extractor", {})
        self.extractor = LlamaExtractor(
            api_key=extractor_config.get("api_key"),
            model=extractor_config.get("openai_model", "gpt-3.5-turbo"),
            schema_path=extractor_config.get("schema_path"),
        )

    def _init_qa_generator(self) -> None:
        """Initialize the QA generator component."""
        qa_config = self.config.get("qa_generator", {})
        self.qa_generator = QAGenerator(
            api_key=qa_config.get("api_key"),
            model=qa_config.get("openai_model", "gpt-3.5-turbo"),
            temperature=qa_config.get("temperature", 0.0),
            max_tokens=qa_config.get("max_tokens", 256),
            batch_size=qa_config.get("batch_size", 5),
        )

    def _init_exporters(self) -> None:
        """Initialize the exporter components."""
        export_config = self.config.get("export", {})
        self.content_exporter = ContentExporter(
            output_path=export_config.get("content_path", "./output/content.json"),
        )
        self.qa_exporter = QAExporter(
            output_path=export_config.get("qa_jsonl_path", "./output/qa.jsonl"),
        )

    def run(
        self,
        input_path: Union[str, Path],
        skip_parse: bool = False,
        skip_extract: bool = False,
        skip_qa: bool = False,
        job_id: Optional[str] = None,
    ) -> None:
        """
        Run the pipeline.

        Args:
            input_path: Path to the input document.
            skip_parse: Whether to skip the parsing stage.
            skip_extract: Whether to skip the extraction stage.
            skip_qa: Whether to skip the QA generation stage.
            job_id: Optional job ID to use for output files. If not provided, will use the input filename.
        """
        start_time = time.time()

        # Create document
        document = Document(input_path)

        # Generate job ID if not provided
        if job_id is None:
            # Use the input filename without extension as the job ID
            job_id = Path(input_path).stem

        logger.info(f"Starting pipeline for input: {input_path} with job ID: {job_id}")

        # Start processing summary
        summary = start_processing_summary(job_id, input_path)

        # Parse document
        chunks = []
        if not skip_parse:
            logger.info("Starting parsing stage")
            summary.start_stage("parsing")
            chunks = self.parser.parse(document, job_id=job_id)
            parsing_duration = summary.end_stage("parsing")
            summary.record_parsing_results(chunks, parsing_duration)
            logger.info(f"Parsing complete: {len(chunks)} chunks extracted")

            # Update content exporter output path with job ID
            content_path = self._get_output_path(self.content_exporter.output_path, job_id)
            content_exporter = ContentExporter(output_path=content_path)

            # Export chunks
            content_exporter.export_chunks(chunks)
            summary.record_output_file("content_json", content_path)
            logger.info(f"Content exported to: {content_path}")

        # Extract statements
        statements = []
        if not skip_extract:
            if skip_parse:
                logger.error("Cannot skip parsing stage if extraction stage is enabled")
                return

            logger.info("Starting extraction stage")
            summary.start_stage("extraction")
            statements = self.extractor.extract(chunks, job_id=job_id)
            extraction_duration = summary.end_stage("extraction")
            summary.record_extraction_results(statements, extraction_duration)
            logger.info(f"Extraction complete: {len(statements)} statements extracted")

        # Generate QA pairs
        if not skip_qa:
            if skip_extract:
                logger.error("Cannot skip extraction stage if QA generation stage is enabled")
                return

            logger.info("Starting QA generation stage")
            summary.start_stage("qa_generation")
            qa_pairs = self.qa_generator.generate(statements, source=str(document.path))
            qa_duration = summary.end_stage("qa_generation")
            summary.record_qa_results(qa_pairs, qa_duration)
            logger.info(f"QA generation complete: {len(qa_pairs)} QA pairs generated")

            # Update QA exporter output path with job ID
            qa_path = self._get_output_path(self.qa_exporter.output_path, job_id)
            qa_exporter = QAExporter(output_path=qa_path)

            # Export QA pairs
            qa_exporter.export(qa_pairs)
            summary.record_output_file("qa_jsonl", qa_path)
            logger.info(f"QA pairs exported to: {qa_path}")

        end_time = time.time()
        logger.info(f"Pipeline completed in {end_time - start_time:.2f} seconds")

        # Finalize and save processing summary
        summary.finalize()
        summary_path = self._get_output_path(Path("./output/summary.json"), job_id)
        summary.save_to_file(summary_path)
        summary.record_output_file("summary_json", summary_path)

        # Display summaries
        summary.print_summary()
        cost_tracker.save_costs()
        cost_tracker.print_summary()

    def _get_output_path(self, original_path: Union[str, Path], job_id: str) -> Path:
        """
        Generate an output path that includes the job ID.

        Args:
            original_path: Original output path.
            job_id: Job ID to include in the path.

        Returns:
            Updated output path with job ID.
        """
        original_path = Path(original_path) if isinstance(original_path, str) else original_path

        # Get the directory and filename
        directory = original_path.parent
        filename = original_path.name

        # Split the filename into name and extension
        name_parts = filename.split('.')
        if len(name_parts) > 1:
            name = '.'.join(name_parts[:-1])
            extension = name_parts[-1]
            new_filename = f"{name}_{job_id}.{extension}"
        else:
            new_filename = f"{filename}_{job_id}"

        # Create the new path
        return directory / new_filename
