"""
Pytest configuration file.
"""

import sys
from unittest.mock import MagicMock

# Disable unused parameter warnings for this file
# pylint: disable=unused-argument

# Create mock modules for external dependencies
MOCK_MODULES = [
    'llama_cloud_services',
    'openai',
]

# Create mock classes
class MockLlamaParse:
    def __init__(self, api_key=None, verbose=False, language="en", num_workers=1):
        pass

    def parse(self, file_path):
        # Return a mock result
        result = MagicMock()

        # Mock the get_markdown_documents method
        mock_doc = MagicMock(
            text="Mock document text",
            metadata={"page": 1, "section": "Introduction"}
        )
        result.get_markdown_documents = MagicMock(return_value=[mock_doc])

        return result

    def aparse(self, file_path):
        # For async version, return the same as sync version
        return self.parse(file_path)

class MockOpenAI:
    def __init__(self, api_key=None):
        self.chat = MagicMock()
        self.chat.completions = MagicMock()

        # Mock the create method to return a response with choices
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = '{"statement": "This is a mock statement", "page": 1}'
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        self.chat.completions.create = MagicMock(return_value=mock_response)

# Create the mock modules
for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = MagicMock()

# Set up specific mock classes
sys.modules['llama_cloud_services'].LlamaParse = MockLlamaParse
sys.modules['openai'].OpenAI = MockOpenAI
