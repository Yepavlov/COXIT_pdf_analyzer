from sqlalchemy.orm import Session
from unstructured.partition.pdf import partition_pdf

from src.app.api.openai_client import OpenAIClient
from src.app.config import get_settings
from src.app.logger_config import logger
from src.app.models.document import Document
from src.app.utils.exceptions import PDFSummaryError

settings = get_settings()
openai_client = OpenAIClient(api_key=settings.openai_api_key, model="gpt-4o-mini")


def get_document_history(db: Session, limit: int = 5) -> list[Document]:
    """Retrieves the latest processed documents from the database."""
    logger.info("LOGIC: Retrieving history from the database...")
    return db.query(Document).order_by(Document.created_at.desc()).limit(limit).all()


def process_and_summarize_pdf(db: Session, file_path: str, filename: str) -> Document:
    """Processes PDF, obtains summary, and saves to database."""
    logger.info(f"LOGIC:  Start processing file {filename}...")
    document_text = _extract_text_from_pdf(file_path)

    if not document_text:
        logger.warning("Unable to extract text from the document.")
        summary_text = "Unable to extract text from the document."
    else:
        logger.info("Obtaining a summary using OpenAIClient...")
        summary_text = openai_client.summarize_text(document_text)

    logger.info(f"Saving the result for the file '{filename}' to the database.")
    db_document = Document(filename=filename, summary=summary_text)

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return db_document


def _extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using unstructured.
    """
    logger.info(f"Start of text extraction from file: {file_path}")
    try:
        elements = partition_pdf(
            filename=file_path,
            strategy="hi_res",
            infer_table_structure=True,
        )
        return "\n\n".join([str(el) for el in elements])
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}", exc_info=True)
        raise PDFSummaryError(
            code="TEXT_EXTRACTION_FAILED",
            message="Unable to extract text from file.",
        )
