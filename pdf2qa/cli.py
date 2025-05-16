"""
Command-line interface for the pdf2qa library.
"""

import os
from pathlib import Path
from typing import Optional

import click

from pdf2qa.pipeline import Pipeline
from pdf2qa.utils.logging import setup_logging


@click.group()
@click.version_option()
def cli():
    """
    pdf2qa: Convert PDFs and other documents into LLM-ready content and Q/A pairs for fine-tuning.
    """
    pass


@cli.command()
@click.option(
    "--input",
    "-i",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Path to the input document (PDF, DOCX, etc.)",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Path to the configuration file (YAML)",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True),
    help="Directory for output files",
)
@click.option(
    "--skip-parse",
    is_flag=True,
    help="Skip the parsing stage",
)
@click.option(
    "--skip-extract",
    is_flag=True,
    help="Skip the extraction stage",
)
@click.option(
    "--skip-qa",
    is_flag=True,
    help="Skip the QA generation stage",
)
@click.option(
    "--job-id",
    "-j",
    type=str,
    help="Job ID to use for output files. If not provided, will use the input filename.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
def process(
    input: str,
    config: Optional[str] = None,
    output_dir: Optional[str] = None,
    skip_parse: bool = False,
    skip_extract: bool = False,
    skip_qa: bool = False,
    job_id: Optional[str] = None,
    verbose: bool = False,
):
    """
    Process a document through the pdf2qa pipeline.
    """
    # Set up logging
    logger = setup_logging(verbose=verbose)

    # Create pipeline
    if config:
        pipeline = Pipeline.from_config(config)
    else:
        pipeline = Pipeline.from_defaults()

    # Update output directory if specified
    if output_dir:
        output_dir_path = Path(output_dir)
        os.makedirs(output_dir_path, exist_ok=True)

        # Update exporters
        pipeline.content_exporter = pipeline.content_exporter.__class__(
            output_path=output_dir_path / "content.json"
        )
        pipeline.qa_exporter = pipeline.qa_exporter.__class__(
            output_path=output_dir_path / "qa.jsonl"
        )

    # Run pipeline
    pipeline.run(
        input_path=input,
        skip_parse=skip_parse,
        skip_extract=skip_extract,
        skip_qa=skip_qa,
        job_id=job_id,
    )


def main():
    """Entry point for the CLI."""
    cli()
