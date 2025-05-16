# Testing pdf2qa

This document provides instructions for testing the pdf2qa library.

## Setup

1. Install the package in development mode:
   ```bash
   pip install -e .
   ```

2. Install test dependencies:
   ```bash
   pip install pytest
   ```

## Running Tests

### Unit Tests

To run all unit tests:
```bash
python -m pytest tests/unit/
```

To run specific test files:
```bash
python -m pytest tests/unit/test_models_simple.py
python -m pytest tests/unit/test_config_simple.py
```

To run tests with verbose output:
```bash
python -m pytest tests/unit/ -v
```

### Test Structure

- `tests/unit/`: Contains unit tests for individual components
- `tests/integration/`: Contains integration tests for the full pipeline
- `tests/conftest.py`: Contains pytest fixtures and mock objects for testing

## Mock Objects

The tests use mock objects to simulate external dependencies like LlamaIndex and OpenAI. This allows the tests to run without requiring actual API keys or making real API calls.

The mock objects are defined in `tests/conftest.py`.

## Adding New Tests

When adding new tests:

1. Create a new test file in the appropriate directory
2. Import the necessary modules and mock objects
3. Write test functions that start with `test_`
4. Run the tests to ensure they pass

## Test Coverage

To generate a test coverage report:
```bash
pip install pytest-cov
python -m pytest --cov=pdf2qa tests/
```

This will show which parts of the code are covered by tests and which are not.

## Integration Testing

For integration testing with real APIs:

1. Set up the required API keys:
   ```bash
   export LLAMA_CLOUD_API_KEY=your_llamaparse_api_key
   export OPENAI_API_KEY=your_openai_api_key
   ```

2. Create a test document (PDF, DOCX, etc.)

3. Run the pipeline:
   ```bash
   python -m pdf2qa.cli process --input test_document.pdf --verbose
   ```

4. Check the output files in the `output/` directory
