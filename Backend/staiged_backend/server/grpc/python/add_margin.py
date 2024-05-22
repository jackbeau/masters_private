import os
import sys
import json
from PyPDF2 import PdfWriter, PdfReader

def add_margin(file_path, margin_side, output_dir):
    input_pdf = PdfReader(file_path)
    output_pdf = PdfWriter()

    MARGIN_SIZE = 200  # Define a large margin size, adjust as needed

    for page_num in range(len(input_pdf.pages)):
        page = input_pdf.pages[page_num]
        media_box = page.mediabox

        if margin_side == 'left':
            new_media_box = (
                media_box.lower_left[0] - MARGIN_SIZE,
                media_box.lower_left[1],
                media_box.upper_right[0],
                media_box.upper_right[1]
            )
            page.mediabox.lower_left = (new_media_box[0], new_media_box[1])
            page.cropbox.lower_left = (new_media_box[0], new_media_box[1])
        elif margin_side == 'right':
            new_media_box = (
                media_box.lower_left[0],
                media_box.lower_left[1],
                media_box.upper_right[0] + MARGIN_SIZE,
                media_box.upper_right[1]
            )
            page.mediabox.upper_right = (new_media_box[2], new_media_box[3])
            page.cropbox.upper_right = (new_media_box[2], new_media_box[3])
        
        output_pdf.add_page(page)

    FILE_NAME = 'output_with_margin.pdf'
    output_file_path = os.path.join(output_dir, FILE_NAME)
    with open(output_file_path, 'wb') as output_file:
        output_pdf.write(output_file)

    return output_file_path

if __name__ == "__main__":
    file_path = sys.argv[1]
    margin_side = sys.argv[2]
    output_dir = sys.argv[3]
    result = add_margin(file_path, margin_side, output_dir)
    print(json.dumps({"file_path": result}))
