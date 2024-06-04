"""
File: pdf_extractor.py
Author: Jack Beaumont
Date: 2024-01-30

Description: Perform OCR of a PDF and extract individual lines.
"""

import fitz
import os
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
