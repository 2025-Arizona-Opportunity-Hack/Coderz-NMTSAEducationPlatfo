"""
PDF Text Extraction Utility
Extracts searchable text from PDF files for Supermemory indexing
"""
import logging
from pathlib import Path
from typing import Optional

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PyPDF2 not installed. PDF text extraction disabled.")

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str, max_pages: int = 50) -> Optional[str]:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Absolute path to PDF file
        max_pages: Maximum number of pages to extract (default 50 to avoid memory issues)
        
    Returns:
        Extracted text as string, or None if extraction fails
    """
    if not PDF_AVAILABLE:
        logger.warning("PyPDF2 not available, skipping PDF text extraction")
        return None
    
    try:
        if not Path(pdf_path).exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return None
        
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        
        # Limit pages to avoid memory issues with large PDFs
        pages_to_extract = min(num_pages, max_pages)
        
        text_parts = []
        for page_num in range(pages_to_extract):
            try:
                page = reader.pages[page_num]
                text = page.extract_text()
                if text and text.strip():
                    text_parts.append(text.strip())
            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num}: {e}")
                continue
        
        if not text_parts:
            logger.warning(f"No text extracted from PDF: {pdf_path}")
            return None
        
        full_text = "\n\n".join(text_parts)
        
        # Limit total text length to avoid overwhelming Supermemory
        max_chars = 10000  # 10k characters ~= 2500 words
        if len(full_text) > max_chars:
            full_text = full_text[:max_chars] + "..."
            logger.info(f"Truncated PDF text to {max_chars} characters")
        
        return full_text
        
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return None


def get_pdf_summary(pdf_path: str) -> str:
    """
    Get a brief summary of PDF content for indexing.
    
    Args:
        pdf_path: Absolute path to PDF file
        
    Returns:
        First few paragraphs or empty string if extraction fails
    """
    full_text = extract_text_from_pdf(pdf_path, max_pages=5)  # Only first 5 pages
    
    if not full_text:
        return ""
    
    # Get first 500 characters as summary
    summary = full_text[:500].strip()
    if len(full_text) > 500:
        # Find last complete sentence
        last_period = summary.rfind('.')
        if last_period > 100:  # Ensure reasonable length
            summary = summary[:last_period + 1]
        else:
            summary += "..."
    
    return summary
