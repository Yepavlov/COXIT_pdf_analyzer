import time

import tiktoken
from openai import APIError, APITimeoutError, OpenAI, RateLimitError

from src.app.config import get_settings
from src.app.logger_config import logger
from src.app.prompts.summarized_prompt import SummarizedPrompt

settings = get_settings()


class OpenAIClient:
    """Client for interacting with OpenAI API."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

        try:
            self.encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            logger.warning(f"Model {model} not found for tiktoken. Using cl100k_base.")
            self.encoding = tiktoken.get_encoding("cl100k_base")

        self.model_context_window = 128000  # For gpt-4o-mini
        self.max_output_tokens = 16000
        self.max_input_tokens = self.model_context_window - self.max_output_tokens

        logger.info(f"Initialized OpenAI client with model: {self.model}")

    def summarize_text(self, text: str) -> str:
        """
        Summarizes a given text. Implements Map-Reduce for large texts.
        This is the main public method of the class.
        """
        token_count = len(self.encoding.encode(text))
        logger.info(
            f"Total tokens in document: {token_count}. Max input tokens: {self.max_input_tokens}."
        )

        if token_count <= self.max_input_tokens:
            logger.info("Document is small enough for a single API call.")
            user_prompt = SummarizedPrompt.USER_PROMPT.format(text=text)
            return self._make_request(SummarizedPrompt.SYSTEM_PROMPT, user_prompt)

        logger.info("Document is too large. Starting Map-Reduce process.")

        tokens = self.encoding.encode(text)
        chunks = self._split_text_on_chunks(tokens)

        logger.info(f"Split text into {len(chunks)} chunks.")

        chunk_summaries = self._summarize_all_chunks(chunks)

        logger.info("Combining chunk summaries for final summarization.")
        combined_summaries = "\n\n".join(chunk_summaries)

        user_prompt_final = SummarizedPrompt.USER_PROMPT_FOR_COMBINING.format(
            combined_summaries=combined_summaries
        )
        final_summary = self._make_request(
            SummarizedPrompt.SYSTEM_PROMPT_COMBINING, user_prompt_final
        )

        return final_summary

    def _make_request(self, system_prompt: str, user_prompt: str) -> str:
        """Handles API requests with retry logic. Returns the text response."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        attempt = settings.attempt
        max_retries = settings.max_retries
        delay = settings.delay
        timeout = settings.timeout
        temperature = settings.temperature

        while attempt < max_retries:
            try:
                logger.info(
                    f"Attempt {attempt + 1}/{max_retries}: Sending request to OpenAI."
                )
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    timeout=timeout,
                )
                content = response.choices[0].message.content
                if content:
                    logger.info("Successfully received response from OpenAI.")
                    return content.strip()
                else:
                    raise ValueError("Received empty content from OpenAI.")

            except (RateLimitError, APITimeoutError, APIError) as e:
                logger.warning(
                    f"API Error on attempt {attempt + 1}: {type(e).__name__} - {e}"
                )
                if attempt >= max_retries - 1:
                    logger.error("Max retries exceeded. Request failed.")
                    raise

                time.sleep(delay)
                delay *= 2
                attempt += 1
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}", exc_info=True)
                raise

        return "Failed to get summary after multiple retries."

    def _split_text_on_chunks(self, tokens: list[int]) -> list[str]:
        """Splits text into chunks based on token count."""
        chunks = []
        for i in range(0, len(tokens), self.max_input_tokens):
            chunk_tokens = tokens[i : i + self.max_input_tokens]
            chunks.append(self.encoding.decode(chunk_tokens))
        return chunks

    def _summarize_all_chunks(self, chunks: list[str]) -> list[str]:
        """Gets a list of summarized chunks."""
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Summarizing chunk {i + 1}/{len(chunks)}...")
            user_prompt_chunk = SummarizedPrompt.USER_PROMPT_CHUNK.format(chunk=chunk)
            summary = self._make_request(
                SummarizedPrompt.SYSTEM_PROMPT_CHUNK, user_prompt_chunk
            )
            chunk_summaries.append(summary)
        return chunk_summaries
