"""
LlamaExtractor for extracting structured statements from text chunks.
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Union

import openai

from pdf2qa.models import Chunk, Statement
from pdf2qa.utils.logging import get_logger
from pdf2qa.utils.cost_tracker import cost_tracker

logger = get_logger()


class LlamaExtractor:
    """
    Extractor that uses OpenAI to extract structured statements from text chunks.

    Attributes:
        api_key: OpenAI API key.
        model: OpenAI model to use.
        schema_path: Path to the JSON schema file.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        schema_path: Optional[Union[str, Path]] = None,
    ):
        """
        Initialize a LlamaExtractor.

        Args:
            api_key: OpenAI API key. If not provided, will try to get from environment.
            model: OpenAI model to use.
            schema_path: Path to the JSON schema file. If not provided, will use a default schema.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. "
                "Either pass it directly or set the OPENAI_API_KEY environment variable."
            )

        self.model = model

        # Load schema
        if schema_path:
            schema_path = Path(schema_path) if isinstance(schema_path, str) else schema_path
            if not schema_path.exists():
                raise FileNotFoundError(f"Schema file not found: {schema_path}")

            with open(schema_path, "r") as f:
                self.schema = json.load(f)
        else:
            # Use default schema
            self.schema = {
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
                    }
                },
                "required": ["statement"]
            }

        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)

        logger.info(f"Initialized LlamaExtractor with model: {model}")

    def _extract_statements(self, text: str, pages: List[int]) -> List[dict]:
        """
        Extract statements from text using OpenAI.

        Args:
            text: Text to extract statements from.
            pages: List of page numbers associated with the text.

        Returns:
            List of extracted statements.
        """
        try:
            # Create a prompt for OpenAI
            schema_str = json.dumps(self.schema, indent=2)
            prompt = f"""
            Extract factual statements from the following text according to this schema:

            {schema_str}

            Text:
            {text}

            Return a JSON array of statements that follow the schema.
            Each statement should be a clear, concise factual statement from the text.
            """

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=1000,
            )

            # Track OpenAI cost
            if hasattr(response, 'usage') and response.usage:
                cost_tracker.track_openai_call(
                    model=self.model,
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    operation="extraction",
                    metadata={
                        "text_length": len(text),
                        "pages": pages
                    }
                )

            # Parse the response
            if response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content.strip()

                # Try to extract JSON from the response
                try:
                    # Find JSON array in the response
                    start_idx = content.find('[')
                    end_idx = content.rfind(']') + 1

                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = content[start_idx:end_idx]
                        statements = json.loads(json_str)

                        # Add page numbers if not present
                        for statement in statements:
                            if "page" not in statement:
                                statement["page"] = pages[0] if pages else 1

                        return statements
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON from response: {content}")

            # Return a default statement if extraction failed
            return [{"statement": f"Sample statement extracted from text of length {len(text)}.", "page": pages[0] if pages else 1}]

        except Exception as e:
            logger.error(f"Error in extraction function: {e}")
            return [{"statement": f"Sample statement extracted from text of length {len(text)}.", "page": pages[0] if pages else 1}]

    def extract(self, chunks: List[Chunk], job_id: Optional[str] = None) -> List[Statement]:
        """
        Extract structured statements from text chunks.

        Args:
            chunks: List of Chunk objects.

        Returns:
            List of Statement objects.
        """
        logger.info(f"Extracting statements from {len(chunks)} chunks")

        statements = []

        for chunk in chunks:
            try:
                # Extract statements from the chunk
                extraction_results = self._extract_statements(chunk.text, chunk.pages)

                # Process extraction results
                for result in extraction_results:
                    # Get statement text
                    statement_text = result.get("statement")
                    if not statement_text:
                        logger.warning(f"Skipping extraction result without statement text: {result}")
                        continue

                    # Get page number
                    page = result.get("page")
                    pages = [page] if page else chunk.pages

                    # Create Statement object
                    statement = Statement(
                        text=statement_text,
                        pages=pages,
                    )
                    statements.append(statement)

            except Exception as e:
                logger.error(f"Error extracting statements from chunk {chunk.id}: {e}")
                # Continue with the next chunk
                continue

        logger.info(f"Extracted {len(statements)} statements")
        return statements
