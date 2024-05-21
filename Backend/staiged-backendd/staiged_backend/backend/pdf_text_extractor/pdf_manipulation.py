import os
from PIL import Image
from pypdf import PdfMerger
import pypdfium2 as pdfium
import numpy as np

def apply_crop_fill_to_ocr_pdf(ocr_pdf_path, output_pdf_path, top_left, bottom_right):
    pdf = pdfium.PdfDocument(ocr_pdf_path)
    n_pages = len(pdf)

    # Create a PdfFileMerger to save the pages into a single PDF
    pdf_merger = PdfMerger()

    for page_number in range(n_pages):
        page = pdf.get_page(page_number)
        pil_image = page.render(
            scale=1,
            rotation=0,
            crop=(0, 0, 0, 0),
            grayscale=False,
        ).to_pil()

        # Convert PIL image to Numpy array
        current_image = np.array(pil_image)

        # Apply crop and fill
        result = crop_and_fill_image(current_image, top_left, bottom_right)

        # Save the result as a new page in a temporary PDF
        result_pdf_path = f"temp_page_{page_number + 1}.pdf"
        Image.fromarray(result.astype(np.uint8)).save(result_pdf_path)

        # Append the result PDF to the PdfFileMerger
        pdf_merger.append(result_pdf_path)

    # Write the merged PDF to the final output PDF
    pdf_merger.write(output_pdf_path)
    pdf_merger.close()

    # Clean up temporary PDF files
    for page_number in range(n_pages):
        temp_pdf_path = f"temp_page_{page_number + 1}.pdf"
        os.remove(temp_pdf_path)

def pdf_image_overlay(input_pdf_path, overlay_output_png_path):
    pdf = pdfium.PdfDocument(input_pdf_path)
    n_pages = len(pdf)

    # Initialize the overlay as None, so we can handle the first image separately
    overlay = None

    # Track the maximum dimensions for resizing
    max_height = 0
    max_width = 0

    for page_number in range(n_pages):
        page = pdf.get_page(page_number)
        pil_image = page.render(
            scale=1,
            rotation=0,
            crop=(0, 0, 0, 0),
            grayscale=False,
        ).to_pil()

        # Convert PIL image to Numpy array
        current_image = np.array(pil_image)

        # Update maximum dimensions
        max_height = max(max_height, current_image.shape[0])
        max_width = max(max_width, current_image.shape[1])

        # If this is the first image, initialize the overlay
        if overlay is None:
            overlay = current_image
        else:
            # Resize both overlay and current_image_resized to the maximum dimensions
            overlay_resized = np.zeros((max_height, max_width, 3), dtype=np.uint8)
            overlay_resized[:overlay.shape[0], :overlay.shape[1], :] = overlay

            current_image_resized = np.zeros((max_height, max_width, 3), dtype=np.uint8)
            current_image_resized[:current_image.shape[0], :current_image.shape[1], :] = current_image

            # Add the current image to the overlay
            overlay = overlay_resized + current_image_resized

    # Convert the Numpy array back to a PIL image for saving
    final_overlay = Image.fromarray(overlay.astype(np.uint8))

    # Save the final overlay as a PNG file
    final_overlay.save(overlay_output_png_path)
