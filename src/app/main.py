"""
Main FastAPI application for PDF Summary AI.
"""

import os.path
from pathlib import Path

import aiofiles
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles

from src.app.utils.helpers import validate_file_or_raise
from src.app.db import database
from src.app.models.shemas import SummaryResponse
from src.app.services.db_service import process_and_summarize_pdf, get_document_history
from src.app.config import get_settings
from src.app.logger_config import logger
from src.app.utils import exceptions

settings = get_settings()

app = FastAPI(
    title="PDF Summary AI",
    description="AI-powered PDF document summarization service",
    version="1.0.0",
    debug=settings.debug,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_path = Path(__file__).parent.parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.exception_handler(exceptions.FileTooLargeError)
async def file_too_large_handler(request: Request, exc: exceptions.FileTooLargeError):
    """Handle custom PDF Summary exception for the case when file too large."""
    logger.warning(exc.message)
    return JSONResponse(status_code=413, content={"message": exc.message})


@app.exception_handler(exceptions.UnsupportedFileTypeError)
async def unsupported_file_type_handler(
    request: Request, exc: exceptions.UnsupportedFileTypeError
):
    """Handle custom PDF Summary exceptions for the case when a file type doesn't support."""
    logger.warning(exc.message)
    return JSONResponse(status_code=400, content={"message": exc.message})


@app.exception_handler(exceptions.PDFSummaryError)
async def pdf_summary_exception_handler(
    request: Request, exc: exceptions.PDFSummaryError
):
    """Handle custom PDF Summary exceptions."""
    logger.error(f"PDF Summary Error: {exc.message}")
    return JSONResponse(status_code=400, content={"message": exc.message})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500, content={"message": "An unexpected error occurred"}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "PDF Summary AI", "version": "1.0.0"}


@app.post("/upload/", response_model=SummaryResponse, tags=["Summarization"])
async def upload_pdf_for_summary(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
):
    """
    Uploads a PDF file, processes it, and returns a summary.
    """
    validate_file_or_raise(file)
    logger.info(f"File received for processing: {file.filename}")
    temp_file_path = os.path.join(settings.upload_dir, file.filename)

    try:
        async with aiofiles.open(temp_file_path, "wb") as buffer:
            while content := await file.read(1024 * 1024):
                await buffer.write(content)

        logger.info(f"The file is temporarily saved at: {temp_file_path}")

        result_doc = await run_in_threadpool(
            process_and_summarize_pdf,
            db=db,
            file_path=str(temp_file_path),
            filename=file.filename,
        )
        return result_doc

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.info(f"Temporary file deleted: {temp_file_path}")


@app.get("/history/", response_model=list[SummaryResponse], tags=["Summarization"])
def get_processing_history(
    db: Session = Depends(database.get_db),
):
    """
    Returns the history of the last 5 processed documents.
    """
    logger.info("Request processing history.")
    history = get_document_history(db=db, limit=5)
    return history


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root():
    """Serve the main HTML page."""
    html_file_path = static_path / "index.html"
    if not html_file_path.exists():
        return HTMLResponse(
            "<h1>Service is running. Frontend file not found.</h1>", status_code=404
        )
    async with aiofiles.open(html_file_path, "r", encoding="utf-8") as f:
        content = await f.read()
    return HTMLResponse(content=content)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
