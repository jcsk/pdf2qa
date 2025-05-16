# pdf2qa: PDF to Q/A Converter

A Python library that ingests PDFs (or other docs), runs them through LlamaParse → LlamaExtract → OpenAI Q/A generation, and exports both "LLM-ready" content JSON and fine-tuning JSONL.

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

## Output

pdf2qa generates two main output files:

1. **Content JSON** (`content.json`): Contains the parsed text chunks with page and section information.

```json
[
  {
    "id": "chunk-1",
    "text": "This is the content of the first chunk.",
    "pages": [1],
    "section": "Introduction"
  },
  ...
]
```

2. **Q/A JSONL** (`qa.jsonl`): Contains question-answer pairs in OpenAI fine-tuning format, one per line.

```jsonl
{"messages":[{"role":"user","content":"What is the main topic of this document?"},{"role":"assistant","content":"The main topic of this document is..."}]}
{"messages":[{"role":"user","content":"What are the key findings?"},{"role":"assistant","content":"The key findings are..."}]}
```

## Custom Statement Extraction

You can customize the statement extraction by providing a custom JSON schema:

```json
{
  "title": "Statement",
  "description": "A factual statement extracted from the text",
  "type": "object",
  "properties": {
    "statement": {
      "type": "string",
      "description": "A clear, concise factual statement from the text"
    },
    "page": {
      "type": "integer",
      "description": "The page number where this statement appears"
    },
    "category": {
      "type": "string",
      "description": "The category of the statement (e.g., fact, opinion, definition)",
      "enum": ["fact", "opinion", "definition", "other"]
    }
  },
  "required": ["statement"]
}
```

## License

MIT
