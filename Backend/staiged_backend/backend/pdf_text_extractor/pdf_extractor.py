"""
File: pdf_extractor.py
Author: Jack Beaumont
Date: 2024-01-30

Description: Perform OCR of a PDF and extract individual lines.
"""

import fitz
import os
import json
from multiprocessing import Process
import ocrmypdf
import logging


class PDFTextExtractor:
    """
    A class to extract text along with Y-axis coordinates and page number from
    a PDF, perform OCR, and save the extraction result as a JSON file.
    """

    def __init__(self, pdf_path):
        """
        Initializes the PDFTextExtractor with the path to the PDF file.

        Parameters:
            pdf_path (str): Path to the PDF file.
        """
        self.pdf_path = pdf_path
        self.ocr_generated = False
        logging.basicConfig(level=logging.INFO)

    def open_pdf(self):
        """Opens the PDF file."""
        if not os.path.isfile(self.pdf_path):
            raise FileNotFoundError(
                f"The file '{self.pdf_path}' does not exist."
            )
        return fitz.open(self.pdf_path)

    def extract_text_with_coordinates(self, clean=True):
        """
        Extracts text along with Y-axis coordinates and page number from the
        PDF. Optionally cleans the result by removing lines with less than 2
        characters and lines containing mostly non-alphanumeric characters.

        Parameters:
            clean (bool, optional): Whether to clean the result. Default is
            True.

        Returns:
            dict: Dictionary containing pages, where each page includes page
                number and a list of lines with Y-coordinate and text.
        """
        result_dict = {"pages": []}

        pdf_doc = self.open_pdf()

        for page_number, page in enumerate(pdf_doc, start=1):
            lines_on_page = []

            blocks = page.get_text("blocks")
            for block in blocks:
                x0, y0, x1, y1 = block[:4]
                b_text: str = block[4]  # Extract the text content
                n_lines = b_text.count('\n')
                dy = (y1 - y0)/n_lines
                l_text = b_text.split('\n')

                for i in range(n_lines):

                    lines_on_page.append({
                        "y_coordinate": y0 + (dy * i),
                        "text": l_text[i]
                    })

            result_dict["pages"].append({
                "page_number": page_number,
                "lines": lines_on_page
            })

        return result_dict

    def save_result_as_json(self, result, output_path=None):
        """
        Saves the extraction result as a JSON file.

        Parameters:
            result (dict): Dictionary containing extracted text with
                coordinates.
            output_path (str, optional): Path to save the JSON file. If not
                provided, the filename will be derived from the PDF path.

        Returns:
            None
        """
        if output_path is None:
            output_path = os.path.splitext(
                self.pdf_path)[0] + "_extracted_data.json"

        with open(output_path, 'w') as json_file:
            json.dump(result, json_file, indent=2, ensure_ascii=False)
        print(f"Result saved to {output_path}")

    @staticmethod
    def ocr_pdf_process(self, output_pdf_path):
        """
        Perform OCR on the PDF using the ocrmypdf library.

        Parameters:
            output_pdf (str): Path to save the OCR'd PDF file.

        Returns:
            None
        """
        ocrmypdf.ocr(self.pdf_path, output_pdf_path)

    @staticmethod
    def delete_file(self, file_path):
        """
        Delete a file if it exists.

        Parameters:
            file_path (str): Path to the file.

        Returns:
            bool: True if the file was deleted successfully, False otherwise.
        """
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        else:
            return False

    def delete_ocr(self):
        """
        Delete the OCR of a PDF.

        Returns:
            bool: True if the OCR was deleted successfully, False otherwise.
        """
        ocr_pdf_path = "ocr_" + self.pdf_path
        if os.path.exists(ocr_pdf_path):
            return self.delete_file(self, ocr_pdf_path)
        elif self.pdf_path.startswith("ocr_"):
            return self.delete_file(self, self.pdf_path)
        else:
            logging.warning("PDF provided does not exist or is not an OCR")
            return False

    def ocr_pdf(self):
        """
        Call the OCR process.

        Parameters:
            None

        Returns:
            output_pdf_path (str): Path to the OCR'd PDF file
        """

        output_pdf_path = "ocr_" + self.pdf_path

        if os.path.isfile(output_pdf_path) is True:
            logging.info("OCR of PDF already exists, skipping OCR generation")

        else:
            p = Process(
                target=self.ocr_pdf_process, args=(self, output_pdf_path)
            )
            p.start()
            p.join()

        return output_pdf_path
