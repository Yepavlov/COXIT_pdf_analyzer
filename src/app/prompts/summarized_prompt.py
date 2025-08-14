class SummarizedPrompt:
    """
    Stores various prompt templates for analyzing and summarizing pdf content.
    """

    SYSTEM_PROMPT = """You are an assistant who creates a concise and clear summary of the provided document text."""

    USER_PROMPT = r"""Create a short summary of the following text:\n\n{text}"""

    SYSTEM_PROMPT_CHUNK = """
    You are an assistant who creates a concise and clear summary of the provided text chunk.
    """
    USER_PROMPT_CHUNK = (
        r"""Create a short summary of the following text chunk:\n\n{chunk}"""
    )

    SYSTEM_PROMPT_COMBINING = """
    You are an assistant who creates a single, final, coherent summary from a collection of individual summaries. Combine them into one fluent, brief text.
    """
    USER_PROMPT_FOR_COMBINING = r"""
    Create a final, consolidated summary from the following list of partial summaries:\n\n{combined_summaries}
    """
