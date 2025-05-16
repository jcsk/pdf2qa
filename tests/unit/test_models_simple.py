"""
Simplified unit tests for the data models.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Test Document class
def test_document():
    """Test the Document model."""
    from pdf2qa.models.document import Document
    
    doc = Document("test.pdf", metadata={"author": "Test Author"})
    assert doc.path.name == "test.pdf"
    assert doc.metadata == {"author": "Test Author"}
    assert doc.file_type == "pdf"

# Test Chunk class
def test_chunk():
    """Test the Chunk model."""
    from pdf2qa.models.chunk import Chunk
    
    chunk = Chunk(
        text="This is a test chunk.",
        pages=[1, 2],
        section="Introduction",
        chunk_id="test-chunk-1",
    )
    assert chunk.id == "test-chunk-1"
    assert chunk.text == "This is a test chunk."
    assert chunk.pages == [1, 2]
    assert chunk.section == "Introduction"
    
    # Test to_dict method
    chunk_dict = chunk.to_dict()
    assert chunk_dict["id"] == "test-chunk-1"
    assert chunk_dict["text"] == "This is a test chunk."
    assert chunk_dict["pages"] == [1, 2]
    assert chunk_dict["section"] == "Introduction"

# Test Statement class
def test_statement():
    """Test the Statement model."""
    from pdf2qa.models.statement import Statement
    
    statement = Statement(
        text="This is a test statement.",
        pages=[1],
        statement_id="test-statement-1",
    )
    assert statement.id == "test-statement-1"
    assert statement.text == "This is a test statement."
    assert statement.pages == [1]
    
    # Test to_dict method
    statement_dict = statement.to_dict()
    assert statement_dict["id"] == "test-statement-1"
    assert statement_dict["text"] == "This is a test statement."
    assert statement_dict["pages"] == [1]

# Test QAPair class
def test_qa_pair():
    """Test the QAPair model."""
    from pdf2qa.models.qa_pair import QAPair
    
    qa_pair = QAPair(
        prompt="What is this test about?",
        completion="This test is about QAPair.",
        pages=[1],
        source="test.pdf",
        chunk_id="test-chunk-1",
        additional_metadata={"category": "test"},
    )
    assert qa_pair.prompt == "What is this test about?"
    assert qa_pair.completion == "This test is about QAPair."
    assert qa_pair.metadata["pages"] == [1]
    assert qa_pair.metadata["source"] == "test.pdf"
    assert qa_pair.metadata["chunk_id"] == "test-chunk-1"
    assert qa_pair.metadata["category"] == "test"
    
    # Test to_dict method
    qa_dict = qa_pair.to_dict()
    assert qa_dict["prompt"] == "What is this test about?"
    assert qa_dict["completion"] == "This test is about QAPair."
    assert qa_dict["metadata"]["pages"] == [1]
    
    # Test to_openai_format method
    openai_format = qa_pair.to_openai_format()
    assert openai_format["messages"][0]["role"] == "user"
    assert openai_format["messages"][0]["content"] == "What is this test about?"
    assert openai_format["messages"][1]["role"] == "assistant"
    assert openai_format["messages"][1]["content"] == "This test is about QAPair."
