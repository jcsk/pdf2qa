# Setup Guide for pdf2qa

## Prerequisites

- Python 3.8 or higher
- LlamaParse API key from [LlamaIndex Cloud](https://cloud.llamaindex.ai/)
- OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)

## Installation

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd pdf2qa
```

2. **Create and activate a virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install the package:**
```bash
pip install -e .
```

## Environment Variables Setup

### Option 1: Using .env file (Recommended for development)

1. **Copy the example environment file:**
```bash
cp .env.example .env
```

2. **Edit the .env file with your actual API keys:**
```bash
# Open .env in your favorite editor
nano .env  # or vim, code, etc.
```

3. **Add your API keys:**
```
LLAMA_CLOUD_API_KEY=llx-your-actual-llamaparse-api-key
OPENAI_API_KEY=sk-your-actual-openai-api-key
```

### Option 2: Export environment variables

```bash
export LLAMA_CLOUD_API_KEY="llx-your-actual-llamaparse-api-key"
export OPENAI_API_KEY="sk-your-actual-openai-api-key"
```

## Getting API Keys

### LlamaParse API Key

1. Go to [LlamaIndex Cloud](https://cloud.llamaindex.ai/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `llx-`)

### OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in
3. Create a new API key
4. Copy the key (starts with `sk-`)

## Verification

Test that everything is working:

```bash
# Check that the CLI is available
pdf2qa --help

# Run tests
pytest tests/

# Test with a sample document (if you have one)
pdf2qa process --input sample.pdf --verbose
```

## Troubleshooting

### API Key Issues

- Make sure your API keys are correctly set in the .env file
- Verify that the .env file is in the project root directory
- Check that there are no extra spaces or quotes around the keys

### Import Errors

- Make sure you've activated your virtual environment
- Reinstall the package: `pip install -e .`

### Permission Errors

- Make sure you have read/write permissions in the project directory
- Check that the output directory exists and is writable

## Security Notes

- Never commit your .env file to version control
- Keep your API keys secure and don't share them
- Consider using different API keys for development and production
- Rotate your API keys regularly
