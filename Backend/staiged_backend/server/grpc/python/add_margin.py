from PyPDF2 import PdfWriter, PdfReader
import sys
import json

def add_margin(file_path, margin_side):
    input_pdf = PdfReader(file_path)
    output_pdf = PdfWriter()

    for page_num in range(len(input_pdf.pages)):
        page = input_pdf.pages[page_num]
        if margin_side == 'left':
            page.mediabox.lower_left = (
                page.mediabox.lower_left[0] - 50,
                page.mediabox.lower_left[1]
            )
        elif margin_side == 'right':
            page.mediabox.lower_right = (
                page.mediabox.lower_right[0] + 50,
                page.mediabox.lower_right[1]
            )
        output_pdf.add_page(page)

    output_file_path = 'output_with_margin.pdf'
    with open(output_file_path, 'wb') as output_file:
        output_pdf.write(output_file)

    return output_file_path

if __name__ == "__main__":
    file_path = sys.argv[1]
    margin_side = sys.argv[2]
    result = add_margin(file_path, margin_side)
    print(json.dumps({"file_path": result}))
