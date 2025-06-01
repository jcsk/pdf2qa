import tempfile
from pdf2qa.parser.llama_parser import LlamaParser
from pdf2qa.models import Document


def test_custom_chunk_settings():
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        doc = Document(f.name)
        parser = LlamaParser(api_key="test", chunk_size=2000, chunk_overlap=100)
        chunks = parser.parse(doc)
        assert parser.chunk_size == 2000
        assert parser.chunk_overlap == 100
        assert len(chunks) == 1
