# pdf2qa

**Transform PDFs into LLM-ready Q&A datasets with comprehensive cost tracking and performance analytics.**

pdf2qa is a production-ready Python library and CLI tool that converts PDF documents into high-quality question-answer pairs for fine-tuning language models. It provides a complete pipeline from document parsing to Q&A generation with detailed cost tracking and performance metrics.

## 🚀 Features

- **📄 Robust PDF Parsing**: Uses LlamaParse for high-quality text extraction with layout preservation
- **🧠 Intelligent Chunking**: Custom text chunking with configurable size and overlap
- **📝 Statement Extraction**: OpenAI-powered extraction of key statements from document chunks
- **❓ Q&A Generation**: Two-stage prompting to generate high-quality question-answer pairs
- **💰 Cost Tracking**: Real-time tracking of API costs for both LlamaParse and OpenAI
- **📊 Performance Analytics**: Detailed metrics on processing time, throughput, and efficiency
- **📁 Multiple Output Formats**: Content JSON, Q&A JSONL, and comprehensive summary reports
- **⚙️ Configurable Pipeline**: Flexible configuration with YAML/JSON support
- **🔄 Robust Error Handling**: Retry logic, rate limiting, and graceful error recovery

## 🏗️ Architecture

```
┌──────────────┐    ┌───────────────┐    ┌─────────────────┐    ┌─────────────┐
│ PDF Document │ →  │ LlamaParse    │ →  │ Statement       │ →  │ Q&A         │
│              │    │ + Chunking    │    │ Extraction      │    │ Generation  │
└──────────────┘    └───────────────┘    └─────────────────┘    └─────┬───────┘
                                                                     │
                                                                     ↓
                                         ┌──────────────────────────────────────┐
                                         │           Outputs                    │
                                         │ • Content JSON (structured chunks)  │
                                         │ • Q&A JSONL (fine-tuning ready)     │
                                         │ • Summary JSON (metrics & costs)    │
                                         │ • Cost tracking (persistent)        │
                                         └──────────────────────────────────────┘
```

## 📦 Installation

```bash
pip install pdf2qa
```

## 🔧 Setup

1. **Set up API keys** in your environment:
```bash
export LLAMA_CLOUD_API_KEY="your-llamaparse-api-key"
export OPENAI_API_KEY="your-openai-api-key"
```

2. **Or use a `.env` file**:
```bash
LLAMA_CLOUD_API_KEY=your-llamaparse-api-key
OPENAI_API_KEY=your-openai-api-key
```

## 🚀 Quick Start

### CLI Usage

```bash
# Basic processing
pdf2qa process --input document.pdf

# With custom configuration
pdf2qa process --input document.pdf --config config.yaml --verbose

# Skip certain stages
pdf2qa process --input document.pdf --skip-extract --skip-qa

# View cost summary
pdf2qa costs

# View processing summary
pdf2qa summary output/summary_document.json
```

### Python API

```python
from pdf2qa import Pipeline

# Create and run pipeline
pipeline = Pipeline()
pipeline.run(input_path="document.pdf")

# With custom configuration
pipeline = Pipeline.from_config("config.yaml")
pipeline.run(input_path="document.pdf", job_id="my-job")
```

## 📊 Example Output

After processing a 14-page PDF document:

```
📊 PROCESSING SUMMARY
================================================================================
🆔 Job ID: ColdCaseSolvability_8.7.19
📄 Document: ColdCaseSolvability_8.7.19.pdf
📏 Size: 2,007,383 bytes (14 pages)

⏱️  Processing Time:
   Total: 310.16s
   Parsing: 15.47s
   Extraction: 66.00s
   QA Generation: 228.68s

📊 Output Metrics:
   Chunks: 34
   Statements: 185
   Q/A Pairs: 185

💰 Cost Breakdown:
   Total: $0.0847
   LlamaParse: $0.0420
   OpenAI: $0.0427 (59,326 tokens)
   Cost per page: $0.0060
   Cost per Q/A pair: $0.0005

🚀 Performance:
   Pages/second: 0.05
   Q/A pairs/second: 0.60

📁 Output Files:
   content_json: output/content_ColdCaseSolvability_8.7.19.json (40.9 KB)
   qa_jsonl: output/qa_ColdCaseSolvability_8.7.19.jsonl (52.3 KB)
   summary_json: output/summary_ColdCaseSolvability_8.7.19.json (1.4 KB)
================================================================================
```

## 📁 Output Files

### 1. Content JSON
Structured chunks with metadata:
```json
[
  {
    "id": "chunk-1",
    "text": "Cold case investigations require systematic approaches...",
    "pages": [1, 2],
    "section": "Introduction"
  }
]
```

### 2. Q&A JSONL
Ready for OpenAI fine-tuning:
```jsonl
{"messages": [{"role": "user", "content": "What are the key factors in cold case solvability?"}, {"role": "assistant", "content": "Key factors include physical evidence preservation, witness availability, and technological advances in forensic analysis."}]}
{"messages": [{"role": "user", "content": "How does DNA evidence impact cold cases?"}, {"role": "assistant", "content": "DNA evidence can provide definitive identification and has revolutionized cold case investigations by enabling matches decades after crimes occurred."}]}
```

### 3. Summary JSON
Comprehensive processing metrics:
```json
{
  "job_id": "document_name",
  "processing_metrics": {
    "total_time_seconds": 310.16,
    "parsing_time_seconds": 15.47
  },
  "cost_metrics": {
    "total_cost_usd": 0.0847,
    "cost_per_page": 0.0060
  }
}
```

## ⚙️ Configuration

Create a `config.yaml` file to customize the pipeline:

```yaml
parser:
  chunk_size: 1500
  chunk_overlap: 200
  language: "en"

extractor:
  model: "gpt-3.5-turbo"
  temperature: 0.0
  max_tokens: 1000

qa_generator:
  model: "gpt-3.5-turbo"
  temperature: 0.0
  max_tokens: 256
  batch_size: 5

export:
  content_path: "./output/content.json"
  qa_path: "./output/qa.jsonl"
```

## 💰 Cost Tracking

pdf2qa provides comprehensive cost tracking and analytics:

### Real-time Cost Monitoring
- **LlamaParse**: $0.003 per page
- **OpenAI**: Variable based on model and token usage
- **Live updates**: See costs accumulate during processing
- **Token counting**: Track input/output tokens for each API call

### Cost Analytics
- **Per-job tracking**: Costs isolated by job ID
- **Service breakdown**: Separate costs for LlamaParse vs OpenAI
- **Model-specific costs**: Track usage by OpenAI model
- **Efficiency metrics**: Cost per page, cost per Q&A pair
- **Historical data**: Persistent cost tracking across runs

### Cost Management
```bash
# View current cost summary
pdf2qa costs

# View costs for specific job
pdf2qa summary output/summary_job_name.json

# Cost data persisted in costs.json
{
  "total_cost": 0.0847,
  "by_service": {
    "llamaparse": {"cost": 0.0420, "calls": 1},
    "openai": {"cost": 0.0427, "calls": 404}
  },
  "by_model": {
    "gpt-3.5-turbo": {"cost": 0.0427, "tokens": 59326}
  }
}
```

## 🔧 CLI Commands

| Command | Description |
|---------|-------------|
| `pdf2qa process` | Process a PDF through the full pipeline |
| `pdf2qa costs` | Display API cost summary |
| `pdf2qa summary` | Display processing summary from file |

### Process Command Options

| Option | Description |
|--------|-------------|
| `--input` | Path to input PDF file |
| `--config` | Path to configuration file |
| `--output-dir` | Output directory (default: ./output) |
| `--skip-parse` | Skip parsing stage |
| `--skip-extract` | Skip extraction stage |
| `--skip-qa` | Skip Q&A generation stage |
| `--verbose` | Enable verbose logging |
| `--job-id` | Custom job identifier |

## 🏗️ Core Components

### Data Models

```python
class Document:
    path: str
    metadata: dict

class Chunk:
    id: str
    text: str
    pages: List[int]
    section: Optional[str]

class Statement:
    id: str
    text: str
    pages: List[int]

class QAPair:
    prompt: str
    completion: str
    metadata: {
        "pages": List[int],
        "source": str,
        "chunk_id": str
    }
```

### Pipeline Stages

1. **Parser Module (LlamaParser)**
   - Uses LlamaParse API for robust PDF→text conversion
   - Produces chunks with page and layout metadata
   - Custom chunking with configurable size and overlap

2. **Extractor Module (LlamaExtractor)**
   - OpenAI-powered statement extraction from chunks
   - Structured extraction with validation
   - Maintains full provenance tracking

3. **QA Generator Module (QAGenerator)**
   - Two-stage prompting: statement → question → answer
   - Batched requests with rate limiting
   - Robust error handling and retries

4. **Export Modules**
   - ContentExporter: Structured JSON with chunks/statements
   - QAExporter: JSONL format ready for OpenAI fine-tuning
   - SummaryGenerator: Comprehensive processing metrics

## 🔧 Error Handling & Logging

- **Retries**: Exponential backoff for transient API errors
- **Validation**: Graceful handling of extraction failures
- **Progress Tracking**: Real-time counts and metrics
- **Cost Monitoring**: Token usage and API cost tracking
- **Verbose Logging**: Detailed pipeline execution logs

## 📦 Dependencies

```
llama-cloud-services>=0.0.11
openai>=1.0.0
pydantic>=2.0.0
click>=8.0.0
python-dotenv>=1.0.0
PyYAML>=6.0.0
tqdm>=4.65.0
```

## 🧪 Development

```bash
# Clone repository
git clone https://github.com/your-username/pdf2qa.git
cd pdf2qa

# Install in development mode
pip install -e .

# Run tests
pytest

# Run with sample document
pdf2qa process --input sample.pdf --verbose
```

## 📋 Requirements

- Python 3.8+
- LlamaParse API key
- OpenAI API key

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [LlamaIndex](https://www.llamaindex.ai/) for LlamaParse
- [OpenAI](https://openai.com/) for language models
- Built with ❤️ for the AI community
