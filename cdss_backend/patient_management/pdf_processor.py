"""
PDF Processor - Extract text from PDF files using PyMuPDF.
Simple implementation for academic presentation.
"""

import fitz  # PyMuPDF


class PDFProcessingError(Exception):
    """Custom exception for PDF processing failures."""
    pass


def extract_text_from_pdf(pdf_file_path):
    """
    Extract all text content from a PDF file.
    
    This function opens a PDF file, reads text from all pages,
    and returns the concatenated text. Simple and easy to explain.
    
    Args:
        pdf_file_path: Absolute path to the PDF file
        
    Returns:
        String containing all text from the PDF (empty if no text found)
        
    Raises:
        PDFProcessingError: If the file cannot be opened or read
    
    Example:
        >>> text = extract_text_from_pdf('/media/lab_reports/report.pdf')
        >>> 'Patient Name: John Doe' in text
        True
    """
    try:
        # Step 1: Open the PDF file
        doc = fitz.open(pdf_file_path)
        
        # Step 2: Extract text from each page
        text = ""
        for page in doc:
            text += page.get_text()
        
        # Step 3: Close the document
        doc.close()
        
        # Step 4: Return the extracted text
        return text
        
    except Exception as e:
        # If anything goes wrong, raise a clear error
        raise PDFProcessingError(f"Failed to extract text: {str(e)}")
