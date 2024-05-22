# import pytesseract
# from pdf2image import convert_from_path
import sys
import json

def perform_ocr(file_path):
    # images = convert_from_path(file_path)
    # text = ''
    
    # for img in images:
    #     text += pytesseract.image_to_string(img)
    
    return file_path

if __name__ == "__main__":
    file_path = sys.argv[1]
    text = perform_ocr(file_path)
    print(json.dumps({"text": text}))
