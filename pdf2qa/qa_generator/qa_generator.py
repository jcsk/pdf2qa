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
from pdf2qa.utils.cost_tracker import cost_tracker

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
    
    def generate(self, statements: List[Statement], source: str, job_id: Optional[str] = None) -> List[QAPair]:
        """
        Generate question-answer pairs from statements.

        Args:
            statements: List of Statement objects.
            source: Source document identifier.
            job_id: Optional job ID for cost tracking.

        Returns:
            List of QAPair objects.
        """
        logger.info(f"Generating Q/A pairs from {len(statements)} statements")
        
        qa_pairs = []
        
        # Process statements in batches
        for i in tqdm(range(0, len(statements), self.batch_size), desc="Generating Q/A pairs"):
            batch = statements[i:i+self.batch_size]

            # Generate questions for the batch
            questions = self._generate_questions(batch, job_id=job_id)

            # Generate answers for the questions
            answers = self._generate_answers(batch, questions, job_id=job_id)
            
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
    
    def _generate_questions(self, statements: List[Statement], job_id: Optional[str] = None) -> List[str]:
        """
        Generate questions from statements.

        Args:
            statements: List of Statement objects.
            job_id: Optional job ID for cost tracking.

        Returns:
            List of questions.
        """
        questions = []
        
        try:
            # Create prompts for each statement
            prompts = []
            for statement in statements:
                prompt = (
    "You will be given a single statement extracted from a technical or investigative document. "
    "Craft exactly one question such that this statement (or a paraphrase of it) would be the correct answer.  \n\n"
    "Requirements for the question:  \n"
    "  1. Do NOT simply copy the statement as‐is. Use synonyms, reword or reframe it.  \n"
    "  2. Vary the question style across these categories (choose one per statement):  \n"
    "     • Fact‐extraction (e.g., “Who…?”, “What is…?”, “When…?”)  \n"
    "     • List extraction (e.g., “List three…”, “Name all the…”)  \n"
    "     • Conceptual/explanatory (e.g., “Explain how…?”, “Why is…?”, “Describe the main…”)  \n"
    "     • Section/lookup (e.g., “On which page would you find…?”, “Where is the section on…?”)  \n"
    "  3. Make sure the question is precise enough so that, if someone reads only the statement, they know exactly how to answer.  \n"
    "  4. Do NOT include the answer text in your question.  \n\n"
    "Examples by category:\n"
    "    • Fact-extraction: 'What method is used for...?'\n"
    "    • List extraction: 'What are the three main components of...?'\n"
    "    • Conceptual: 'How does the process of... work?'\n"
    "    • Section/lookup: 'In which section would you find information about...?'\n\n"
    f"Statement:\n{statement.text}\n\n"
    "Deliverable:\n[Only the question, no additional commentary or answer]"
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

                # Track OpenAI cost for question generation
                if hasattr(response, 'usage') and response.usage:
                    cost_tracker.track_openai_call(
                        model=self.model,
                        input_tokens=response.usage.prompt_tokens,
                        output_tokens=response.usage.completion_tokens,
                        operation="question_generation",
                        job_id=job_id,
                        metadata={"batch_size": len(prompts)}
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
    
    def _generate_answers(self, statements: List[Statement], questions: List[str], job_id: Optional[str] = None) -> List[str]:
        """
        Generate answers from statements and questions.

        Args:
            statements: List of Statement objects.
            questions: List of questions.
            job_id: Optional job ID for cost tracking.

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
    "You have a statement and a question. Your job is to produce a single, direct answer "
    "that uses ONLY the information from the statement.  \n\n"
    "Answer requirements:  \n"
    "  1. If the question asks for a single fact, answer in one concise sentence.  \n"
    "  2. If the question asks for a list, enumerate each item clearly (e.g., “• Item 1; • Item 2; …”).  \n"
    "  3. If the question asks for explanation or summary, answer in 2–3 sentences at most, "
    "     strictly based on the statement’s content—no outside knowledge or conjecture.  \n"
    "  4. Do NOT add any information beyond what’s in the statement.  \n"
    "  5. If the statement doesn't fully answer the question, respond with only what can be determined from the statement and note any limitations.\n\n"
    f"Statement:\n{statement.text}\n\n"
    f"Question:\n{question}\n\n"
    "Deliverable:\n[Only the answer text, no extra commentary]"
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

                # Track OpenAI cost for answer generation
                if hasattr(response, 'usage') and response.usage:
                    cost_tracker.track_openai_call(
                        model=self.model,
                        input_tokens=response.usage.prompt_tokens,
                        output_tokens=response.usage.completion_tokens,
                        operation="answer_generation",
                        job_id=job_id,
                        metadata={"batch_size": len(prompts)}
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
