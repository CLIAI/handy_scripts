#!/usr/bin/env python3

# OCR with Tesseract including enhancing options leverages adaptive and
# simple thresholding to boost text extraction accuracy; employs
# preprocessing for grayscale conversion and bounding box details as
# differentiators; core features include user-configurable options for
# grayscale, thresholding, OCR engine, page segmentation, and language
# support; with additional functionalities like auto-preprocessing and
# bounding box extraction, this tool provides detailed text recognition
# data while ensuring ease of use through command-line interface.
#
# published:
# * https://github.com/CLIAI/handy_scripts/blob/main/ocr_tesseract.py
# * https://gist.github.com/gwpl/aa26593b575c93c76178a1bcc2afa9eb
#
# Keep sources:
# * https://x.com/i/grok/share/mbO9qX38FWwWq1CvRMvG4rpeJ
# * https://chatgpt.com/share/67c9e100-84d4-8007-b9ef-c44c419e7e13
# * https://www.phind.com/search/cm7xn42px00002v6s3gh7xg8e


import sys
import argparse
from PIL import Image

# Try to import required libraries with helpful error messages if they fail
try:
    import cv2
except ImportError:
    print("ERROR: import cv2 failed")
    print("For ArchLinux users, you may want to install:")
    print("# sudo pacman -S python-opencv opencv-samples opencv")
    print("For other distributions, use your package manager or pip:")
    print("# pip install opencv-python")
    sys.exit(1)

try:
    import pytesseract
except ImportError:
    print("ERROR: import pytesseract failed")
    print("For ArchLinux users, you may want to install:")
    print("# sudo pacman -S python-pytesseract python-pyocr")
    print("For other distributions, use your package manager or pip:")
    print("# pip install pytesseract")
    sys.exit(1)

def preprocess_image(image, grayscale=True, threshold=False, threshold_value=150, adaptive=False):
    """Preprocess the image with specified options."""
    processed = image.copy()
    if grayscale:
        processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
    if threshold:
        if adaptive:
            processed = cv2.adaptiveThreshold(processed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        else:
            _, processed = cv2.threshold(processed, threshold_value, 255, cv2.THRESH_BINARY)
    return processed

def perform_ocr(image_path, preprocess_options, tesseract_config, return_bounding_boxes=False):
    """Run OCR on the image with the given settings."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Unable to load image at {image_path}")
    processed_image = preprocess_image(image, **preprocess_options)
    pil_image = Image.fromarray(processed_image)
    extracted_text = pytesseract.image_to_string(pil_image, config=tesseract_config)
    output = {"text": extracted_text}
    if return_bounding_boxes:
        data = pytesseract.image_to_data(pil_image, config=tesseract_config, output_type=pytesseract.Output.DICT)
        output["data"] = data
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tesseract OCR with Preprocessing Options")
    parser.add_argument("image_path", type=str, help="Path to the image file")
    parser.add_argument("--grayscale", type=bool, default=True, help="Convert image to grayscale")
    parser.add_argument("--threshold", type=bool, default=True, help="Apply simple thresholding")
    parser.add_argument("--threshold_value", type=int, default=150, help="Threshold value for simple thresholding")
    parser.add_argument("--adaptive", type=bool, default=False, help="Use adaptive thresholding")
    parser.add_argument("--psm", type=int, default=3, help="Page segmentation mode for Tesseract")
    parser.add_argument("--oem", type=int, default=3, help="OCR Engine mode for Tesseract")
    parser.add_argument("--language", type=str, default="eng", help="Language for OCR")
    parser.add_argument("--bounding_boxes", action="store_true", help="Return bounding box information")
    parser.add_argument("--auto_preprocess", action="store_true", help="Automatically use adaptive thresholding")
    args = parser.parse_args()

    tesseract_config = f"--psm {args.psm} --oem {args.oem} -l {args.language}"
    preprocess_options = {
        "grayscale": args.grayscale,
        "threshold": args.threshold,
        "threshold_value": args.threshold_value,
        "adaptive": args.adaptive or args.auto_preprocess
    }

    result = perform_ocr(args.image_path, preprocess_options, tesseract_config, args.bounding_boxes)
    print("Extracted Text:", result["text"])
    if args.bounding_boxes:
        print("\nBounding Box Data:")
        for i in range(len(result["data"]["text"])):
            if result["data"]["text"][i].strip():
                print(f"Text: '{result['data']['text'][i]}' | Box: [{result['data']['left'][i]}, {result['data']['top'][i]}, {result['data']['width'][i]}, {result['data']['height'][i]}] | Confidence: {result['data']['conf'][i]}")
