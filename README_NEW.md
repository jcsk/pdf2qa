# pdf2qa: PDF to Q/A Converter

A Python library that ingests PDFs (or other docs), runs them through LlamaParse → LlamaExtract → OpenAI Q/A generation, and exports both "LLM-ready" content JSON and fine-tuning JSONL.

## Project Overview

pdf2qa provides a pip-installable CLI and Python API to turn any PDF (or text document) into:
1. Content JSON – cleaned, chunked text with full provenance
2. Q/A JSONL – ready to feed into OpenAI's fine-tuning API

It leverages:
- LlamaParse (via llamaindex SDK) for robust PDF→text parsing
- LlamaExtract (via llamaindex SDK) for schema-driven statement extraction
- OpenAI APIs for question-answer generation

## Installation

```bash
pip install pdf2qa
```

## Requirements

- Python 3.8+
- LlamaParse API key (for document parsing)
- OpenAI API key (for statement extraction and Q/A generation)

## Quick Start

### Command Line

```bash
# Set API keys
export LLAMA_CLOUD_API_KEY=your_llamaparse_api_key
export OPENAI_API_KEY=your_openai_api_key

# Process a document with default settings
pdf2qa process --input document.pdf

# Process with custom configuration
pdf2qa process --input document.pdf --config config.yaml

# Process with custom output directory
pdf2qa process --input document.pdf --output-dir ./my_output

# Process with a specific job ID
pdf2qa process --input document.pdf --job-id my_job_123

# Skip certain stages
pdf2qa process --input document.pdf --skip-qa

# Custom chunking
pdf2qa process --input document.pdf --chunk-size 2000 --chunk-overlap 100
```

### Python API

```python
import os
from pdf2qa import Pipeline

# Set API keys
os.environ["LLAMA_CLOUD_API_KEY"] = "your_llamaparse_api_key"
os.environ["OPENAI_API_KEY"] = "your_openai_api_key"

# Create pipeline with default configuration
pipeline = Pipeline.from_defaults()

# Or create pipeline from configuration file
pipeline = Pipeline.from_config("config.yaml")

# Run the pipeline
pipeline.run(input_path="document.pdf")

# Run with a specific job ID
pipeline.run(input_path="document.pdf", job_id="my_job_123")
```

## Configuration

You can customize the behavior of pdf2qa using a YAML configuration file:

```yaml
parser:
  language: "en"
  api_key_env: "LLAMA_CLOUD_API_KEY"
  chunk_size: 1500
  chunk_overlap: 200

extractor:
  openai_model: "gpt-3.5-turbo"
  schema_path: "./schemas/statement.json"
  api_key_env: "OPENAI_API_KEY"

qa_generator:
  openai_model: "gpt-3.5-turbo"
  temperature: 0.0
  max_tokens: 256
  batch_size: 5
  api_key_env: "OPENAI_API_KEY"

export:
  content_path: "./output/content.json"
  qa_jsonl_path: "./output/qa.jsonl"
```

## Core Architecture

```
┌──────────────┐    ┌───────────────┐    ┌─────────────────┐    ┌─────────────┐
│ PDF / DOC/X  │ →  │ Parser Module │ →  │ Extractor Module│ →  │ QA Generator│
└──────────────┘    └───────────────┘    └─────────────────┘    └─────┬───────┘
                                                                     │
                                                                     ↓
                                                   ┌──────────────────────────┐
                                                   │   Exporters & CLI        │
                                                   │ └ Content JSON           │
                                                   │ └ Q/A JSONL              │
                                                   └──────────────────────────┘
```

## Testing

For information on testing the library, see [TESTING.md](TESTING.md).

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/yourusername/pdf2qa.git
cd pdf2qa

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest black isort mypy
```

## License

MIT
