"""
File: __init__.py
Author: Jack Beaumont
Date: 2024-01-26

Description: Convert pdf document to JSON array contextually encoding page and
line data.
"""

import json
import sys

from pdf_text_extractor import PDFTextExtractor


def perfom_ocr(file_path):
    try:
        output_file_path = PDFTextExtractor(file_path).ocr_pdf()
        return output_file_path
    except FileNotFoundError as file_not_found_error:
        print(f"Error: {file_not_found_error}")
    except Exception as other_error:
        print(f"An unexpected error occurred: {other_error}")


if __name__ == "__main__":
    file_path = sys.argv[1]
    result = perfom_ocr(file_path)
    print(json.dumps({"file_path": result}))
