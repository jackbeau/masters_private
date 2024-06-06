"""
Author: Jack Beaumont
Date: 06/06/2024

This script adds a margin to PDF files. The margin can be added to the left or
right side of the pages.
"""

import os
import sys
import json
import logging
from PyPDF2 import PdfWriter, PdfReader, PageObject

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def add_margin(file_path: str, margin_side: str, output_dir: str) -> str:
    """
    Adds a margin to each page of a PDF file.

    Parameters:
    file_path (str): The path to the input PDF file.
    margin_side (str): The side to which the margin should be added
                       ('left' or 'right').
    output_dir (str): The directory where the output PDF file will be saved.

    Returns:
    str: The path to the output PDF file with the added margin.
    """
    logging.info(f"Starting to add margin to the PDF file: {file_path}")

    input_pdf = PdfReader(file_path)
    output_pdf = PdfWriter()
    MARGIN_SIZE = 200  # Define a large margin size, adjust as needed

    for page_num in range(len(input_pdf.pages)):
        page = input_pdf.pages[page_num]
        media_box = page.mediabox

        if margin_side == "left":
            new_media_box = (
                media_box.lower_left[0] - MARGIN_SIZE,
                media_box.lower_left[1],
                media_box.upper_right[0],
                media_box.upper_right[1],
            )
            page.mediabox.lower_left = (new_media_box[0], new_media_box[1])
            page.cropbox.lower_left = (new_media_box[0], new_media_box[1])
        elif margin_side == "right":
            new_media_box = (
                media_box.lower_left[0],
                media_box.lower_left[1],
                media_box.upper_right[0] + MARGIN_SIZE,
                media_box.upper_right[1],
            )
            page.mediabox.upper_right = (new_media_box[2], new_media_box[3])
            page.cropbox.upper_right = (new_media_box[2], new_media_box[3])
        else:
            logging.warning(
                f"Invalid margin_side '{margin_side}' specified. "
                "Returning original file."
            )
            new_media_box = (
                media_box.lower_left[0],
                media_box.lower_left[1],
                media_box.upper_right[0],
                media_box.upper_right[1],
            )
            page.mediabox.upper_right = (new_media_box[2], new_media_box[3])
            page.cropbox.upper_right = (new_media_box[2], new_media_box[3])

        try:
            output_pdf.add_page(page)
        except AssertionError as e:
            logging.error(
                f"Error adding page {page_num}: {e}. "
                "Attempting to create a new page object."
            )
            new_page = PageObject.create_blank_page(
                width=page.mediabox.width, height=page.mediabox.height
            )
            new_page.merge_page(page)
            output_pdf.add_page(new_page)

    FILE_NAME = "output_with_margin.pdf"
    output_file_path = os.path.join(output_dir, FILE_NAME)
    with open(output_file_path, "wb") as output_file:
        output_pdf.write(output_file)

    logging.info(
        f"PDF file with margin added successfully saved to: {output_file_path}"
    )
    return output_file_path


if __name__ == "__main__":
    if len(sys.argv) != 4:
        logging.error(
            "Invalid number of arguments."
            "Usage: <script> <file_path> <margin_side> <output_dir>"
        )
        sys.exit(1)

    file_path = sys.argv[1]
    margin_side = sys.argv[2]
    output_dir = sys.argv[3]

    result = add_margin(file_path, margin_side, output_dir)
    logging.info("Process completed successfully.")
    print(json.dumps({"file_path": result}))
