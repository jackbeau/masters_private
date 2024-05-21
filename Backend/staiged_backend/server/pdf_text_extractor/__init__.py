"""
File: __init__.py
Author: Jack Beaumont
Date: 2024-01-26

Description: Convert pdf document to JSON array contextually encoding page and
line data.
"""

from pdf_extractor import PDFTextExtractor
from image_processing import crop_and_fill_image, get_max_coordinates
from pdf_manipulation import apply_crop_fill_to_ocr_pdf, pdf_image_overlay

if __name__ == "__main__":
    input_pdf_path = "input.pdf"

    try:
        pdf_extractor = PDFTextExtractor(input_pdf_path)
        # pdf_extractor.delete_ocr()
        # pdf_extractor.pdf_path = pdf_extractor.ocr_pdf()
        extraction_result = pdf_extractor.extract_text_with_coordinates()
        pdf_extractor.save_result_as_json(extraction_result)

        # Additional functionality can be called here as needed
        # For example:
        # crop_and_fill_image("input.pdf", "output.pdf")

    except FileNotFoundError as file_not_found_error:
        print(f"Error: {file_not_found_error}")
    except Exception as other_error:
        print(f"An unexpected error occurred: {other_error}")
