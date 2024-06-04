"""
File: __init__.py
Author: Jack Beaumont
Date: 2024-01-26

Description: Convert pdf document to JSON array contextually encoding page and
line data.
"""

from server.grpc.python.pdf_utils.perform_ocr.pdf_text_extractor import PDFTextExtractor

    

def perforn_ocr(file_path):
    try:
        pdf_extractor = PDFTextExtractor(file_path).ocr_pdf()
        return file_path
    except FileNotFoundError as file_not_found_error:
        print(f"Error: {file_not_found_error}")
    except Exception as other_error:
        print(f"An unexpected error occurred: {other_error}")
