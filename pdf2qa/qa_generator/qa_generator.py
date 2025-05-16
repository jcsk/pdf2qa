"""
QAGenerator for generating question-answer pairs from statements.
"""

import logging
import os
import time
from typing import Dict, List, Optional

import openai
from tqdm import tqdm

from pdf2qa.models import QAPair, Statement
from pdf2qa.utils.logging import get_logger

logger = get_logger()


class QAGenerator:
    """
    Generator that uses OpenAI's API to generate question-answer pairs from statements.
    
    Attributes:
        api_key: OpenAI API key.
        model: OpenAI model to use.
        temperature: Temperature for generation.
        max_tokens: Maximum number of tokens to generate.
        batch_size: Number of statements to process in a batch.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.0,
        max_tokens: int = 256,
        batch_size: int = 5,
    ):
        """
        Initialize a QAGenerator.
        
        Args:
            api_key: OpenAI API key. If not provided, will try to get from environment.
            model: OpenAI model to use.
            temperature: Temperature for generation.
            max_tokens: Maximum number of tokens to generate.
            batch_size: Number of statements to process in a batch.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. "
                "Either pass it directly or set the OPENAI_API_KEY environment variable."
            )
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.batch_size = batch_size
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        
        logger.info(
            f"Initialized QAGenerator with model: {model}, "
            f"temperature: {temperature}, max_tokens: {max_tokens}, "
            f"batch_size: {batch_size}"
        )
    
    def generate(self, statements: List[Statement], source: str) -> List[QAPair]:
        """
        Generate question-answer pairs from statements.
        
        Args:
            statements: List of Statement objects.
            source: Source document identifier.
            
        Returns:
            List of QAPair objects.
        """
        logger.info(f"Generating Q/A pairs from {len(statements)} statements")
        
        qa_pairs = []
        
        # Process statements in batches
        for i in tqdm(range(0, len(statements), self.batch_size), desc="Generating Q/A pairs"):
            batch = statements[i:i+self.batch_size]
            
            # Generate questions for the batch
            questions = self._generate_questions(batch)
            
            # Generate answers for the questions
            answers = self._generate_answers(batch, questions)
            
            # Create QAPair objects
            for j, statement in enumerate(batch):
                if j >= len(questions) or j >= len(answers):
                    logger.warning(f"Skipping statement due to missing question or answer: {statement.text[:50]}...")
                    continue
                
                question = questions[j]
                answer = answers[j]
                
                qa_pair = QAPair(
                    prompt=question,
                    completion=answer,
                    pages=statement.pages,
                    source=source,
                    chunk_id=statement.id,
                )
                qa_pairs.append(qa_pair)
            
            # Sleep to avoid rate limits
            if i + self.batch_size < len(statements):
                time.sleep(1)
        
        logger.info(f"Generated {len(qa_pairs)} Q/A pairs")
        return qa_pairs
    
    def _generate_questions(self, statements: List[Statement]) -> List[str]:
        """
        Generate questions from statements.
        
        Args:
            statements: List of Statement objects.
            
        Returns:
            List of questions.
        """
        questions = []
        
        try:
            # Create prompts for each statement
            prompts = []
            for statement in statements:
                prompt = (
                    "Generate a clear, specific question that would have the following statement as its answer. "
                    "The question should be detailed enough that this statement would be the expected answer. "
                    "Do not include the answer in your response, only the question.\n\n"
                    f"Statement: {statement.text}\n\n"
                    "Question:"
                )
                prompts.append(prompt)
            
            # Call OpenAI API
            responses = []
            for prompt in prompts:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                responses.append(response)
            
            # Extract questions from responses
            for response in responses:
                if response.choices and response.choices[0].message.content:
                    question = response.choices[0].message.content.strip()
                    questions.append(question)
                else:
                    questions.append("")
        
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            # Return empty questions for the failed batch
            questions = [""] * len(statements)
        
        return questions
    
    def _generate_answers(self, statements: List[Statement], questions: List[str]) -> List[str]:
        """
        Generate answers from statements and questions.
        
        Args:
            statements: List of Statement objects.
            questions: List of questions.
            
        Returns:
            List of answers.
        """
        answers = []
        
        try:
            # Create prompts for each statement and question
            prompts = []
            for statement, question in zip(statements, questions):
                if not question:
                    prompts.append("")
                    continue
                
                prompt = (
                    "Given the following statement and question, provide a clear, concise answer "
                    "based only on the information in the statement. Do not add any information "
                    "that is not present in the statement.\n\n"
                    f"Statement: {statement.text}\n\n"
                    f"Question: {question}\n\n"
                    "Answer:"
                )
                prompts.append(prompt)
            
            # Call OpenAI API
            responses = []
            for prompt in prompts:
                if not prompt:
                    responses.append(None)
                    continue
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                responses.append(response)
            
            # Extract answers from responses
            for response in responses:
                if response and response.choices and response.choices[0].message.content:
                    answer = response.choices[0].message.content.strip()
                    answers.append(answer)
                else:
                    answers.append("")
        
        except Exception as e:
            logger.error(f"Error generating answers: {e}")
            # Return empty answers for the failed batch
            answers = [""] * len(statements)
        
        return answers
