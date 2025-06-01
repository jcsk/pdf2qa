Below is a high-level spec for a Python library, pdf2qa, that ingests PDFs (or other docs), runs them through LlamaParse → LlamaExtract → OpenAI Q/A generation, and exports both “LLM-ready” content JSON and fine-tuning JSONL.

⸻

1. Project Overview

pdf2qa provides a pip-installable CLI and Python API to turn any PDF (or text document) into:
	1.	Content JSON – cleaned, chunked text with full provenance
	2.	Q/A JSONL – ready to feed into OpenAI’s fine-tuning API

It leverages:
	•	LlamaParse (via llamaindex SDK) for robust PDF→text parsing
	•	LlamaExtract (via llamaindex SDK) for schema-driven statement extraction
	•	OpenAI APIs for question-answer generation

⸻

2. Core Architecture

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


⸻

3. Components & Data Models

3.1 Data Models
	•	Document

class Document:
    path: str
    metadata: dict


	•	Chunk

class Chunk:
    id: str
    text: str
    pages: List[int]
    section: Optional[str]


	•	Statement

class Statement:
    id: str
    text: str
    pages: List[int]


	•	QAPair

class QAPair:
    prompt: str
    completion: str
    metadata: {
      "pages": List[int],
      "source": str,
      "chunk_id": str
    }



3.2 Parser Module
	•	LlamaParser
	•	Inputs: Document.path
	•	Uses llamaindex’s LlamaParse API to produce a list of raw text chunks with page and layout metadata.
	•	Outputs: List[Chunk] (text only, minimal cleaning done by LlamaParse).

3.3 Extractor Module
	•	LlamaExtractor
	•	Inputs: List[Chunk] + user-defined Pydantic/JSON Schema (e.g. { statement: str, page: int }).
	•	Calls llamaindex’s LlamaExtract to produce List[Statement].
	•	Ensures structured, validated extraction of “ideas,” with provenance.

3.4 QA Generator Module
	•	QAGenerator
	•	Inputs: List[Statement]
	•	Two-stage prompting against OpenAI’s ChatCompletion endpoint:
	1.	Statement → question
	2.	Statement + question → answer
	•	Batches requests, handles rate limits & retries.
	•	Outputs: List[QAPair]

3.5 Exporters
	•	ContentExporter
	•	Persists parsed chunks (and/or statements) to a JSON file:

[
  { "id":"chunk-1", "text":"…", "pages":[1], "section":null },
  …
]


	•	QAJExporter
	•	Writes Q/A pairs as JSONL, one object per line, ready for OpenAI fine-tuning.

⸻

4. Configuration

Use a YAML (or JSON) config to tune behavior:

parser:
  model: "llama-parse-1"
  api_key_env: "LLAMAINDEX_API_KEY"
  chunk_size: 1500
  chunk_overlap: 200

extractor:
  agent_id: "statement-extraction-v1"
  schema_path: "./schemas/statement.json"

qa_generator:
  openai_model: "gpt-3.5-turbo"
  temperature: 0.0
  max_tokens: 256
  batch_size: 5
  api_key_env: "OPENAI_API_KEY"

export:
  content_path: "./output/content.json"
  qa_jsonl_path: "./output/qa.jsonl"


⸻

5. CLI Design

$ pip install pdf2qa

# Basic pipeline
$ pdf2qa process --input Book.pdf --config config.yaml

# Options
--input       Path to PDF/DOCX
--config      YAML config file
--output-dir  Directory for JSON + JSONL
--skip-parse  [skip parser stage]
--skip-extract
--skip-qa
--verbose
--chunk-size [tokens]
--chunk-overlap [tokens]

Under the hood, process orchestrates:

from pdf2qa import Pipeline

pipe = Pipeline.from_config("config.yaml")
pipe.run(input_path="Book.pdf")
# writes content.json and qa.jsonl


⸻

6. Error Handling & Logging
	•	Retries on transient API errors (exponential back-off)
	•	Validation failures in extractor emit warnings and drop bad records
	•	Progress logging with counts: pages parsed, statements extracted, Q/A generated
	•	Metrics: time per stage, tokens used (for cost tracking)

⸻

7. Dependencies

llamaindex>=0.x
openai>=0.x
pydantic>=1.x
PyMuPDF or pdfminer.six
click (for CLI)
tqdm (for progress bars)


⸻

Next Steps
	1.	Define JSON Schema for “Statement” extraction.
	2.	Prototype the LlamaParser + LlamaExtractor integration.
	3.	Implement batched OpenAI Q/A prompting with robust error handling.
	4.	Build CLI and config loader.
	5.	Write end-to-end tests on a short sample PDF.

With this spec in hand, you can start scaffolding the repo, iterating on prompts and schemas, and delivering a turnkey toolkit for turning any document into fine-tuning-ready datasets.