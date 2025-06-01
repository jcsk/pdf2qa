"""
Command-line interface for the pdf2qa library.
"""

import os
from pathlib import Path
from typing import Optional

import click

from pdf2qa.pipeline import Pipeline
from pdf2qa.utils.logging import setup_logging
from pdf2qa.utils.cost_tracker import cost_tracker


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
    "--chunk-size",
    type=int,
    help="Number of tokens per chunk when parsing",
)
@click.option(
    "--chunk-overlap",
    type=int,
    help="Number of overlapping tokens between chunks",
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
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
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

    # Override chunking settings if provided
    if chunk_size is not None:
        pipeline.parser.chunk_size = chunk_size
    if chunk_overlap is not None:
        pipeline.parser.chunk_overlap = chunk_overlap

    # Run pipeline
    pipeline.run(
        input_path=input,
        skip_parse=skip_parse,
        skip_extract=skip_extract,
        skip_qa=skip_qa,
        job_id=job_id,
    )


@cli.command()
@click.option(
    "--cost-file",
    default="costs.json",
    help="Path to the cost tracking file.",
)
def costs(cost_file: str):
    """
    Display API cost summary.
    """
    from pdf2qa.utils.cost_tracker import CostTracker

    tracker = CostTracker(cost_file)
    tracker.print_summary()


@cli.command()
@click.argument("summary_file", type=click.Path(exists=True))
def summary(summary_file: str):
    """
    Display processing summary from a summary file.
    """
    import json

    try:
        with open(summary_file, 'r') as f:
            data = json.load(f)

        print("\n" + "="*80)
        print("📊 PROCESSING SUMMARY")
        print("="*80)
        print(f"🆔 Job ID: {data['job_id']}")
        print(f"📄 Document: {data['input_document']['path']}")
        print(f"📏 Size: {data['input_document']['size_bytes']:,} bytes ({data['input_document']['estimated_pages']} pages)")

        metrics = data['processing_metrics']
        print(f"\n⏱️  Processing Time:")
        print(f"   Total: {metrics['total_time_seconds']:.2f}s")
        print(f"   Parsing: {metrics['parsing_time_seconds']:.2f}s")
        print(f"   Extraction: {metrics['extraction_time_seconds']:.2f}s")
        print(f"   QA Generation: {metrics['qa_generation_time_seconds']:.2f}s")

        output = data['output_metrics']
        print(f"\n📊 Output Metrics:")
        print(f"   Chunks: {output['chunks_created']}")
        print(f"   Statements: {output['statements_extracted']}")
        print(f"   Q/A Pairs: {output['qa_pairs_generated']}")

        costs = data['cost_metrics']
        print(f"\n💰 Cost Breakdown:")
        print(f"   Total: ${costs['total_cost_usd']:.4f}")
        print(f"   LlamaParse: ${costs['llamaparse_cost_usd']:.4f}")
        print(f"   OpenAI: ${costs['openai_cost_usd']:.4f} ({costs['openai_tokens_used']:,} tokens)")
        print(f"   Cost per page: ${costs['cost_per_page']:.4f}")
        print(f"   Cost per Q/A pair: ${costs['cost_per_qa_pair']:.4f}")

        perf = data['performance_metrics']
        print(f"\n🚀 Performance:")
        print(f"   Pages/second: {perf['pages_per_second']:.2f}")
        print(f"   Q/A pairs/second: {perf['qa_pairs_per_second']:.2f}")

        print(f"\n📁 Output Files:")
        for file_type, info in data['output_files'].items():
            size_kb = info["size_bytes"] / 1024
            print(f"   {file_type}: {info['path']} ({size_kb:.1f} KB)")

        print("="*80)

    except Exception as e:
        click.echo(f"Error reading summary file: {e}", err=True)


def main():
    """Entry point for the CLI."""
    cli()
