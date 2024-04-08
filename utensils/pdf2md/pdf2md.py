#!/usr/bin/env python3

import sys
import os
import argparse
import fitz  # PyMuPDF

def convert_pdf_to_markdown(pdf_path):
    try:
        # Load the PDF file
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Failed to read PDF file: {e}")
        return

    # Initialize Markdown content
    md_content = ""

    # Iterate through each page of the PDF
    for page_num in range(len(doc)):
        # Get the page
        page = doc.load_page(page_num)
        # Extract text from the page
        text = page.get_text("text")
        # Add the text to our Markdown content
        md_content += text + "\n\n"

    if not md_content:
        print("No readable document items found in the PDF file.")
        return

    # Generate output file path
    md_path = os.path.splitext(pdf_path)[0] + ".md"
    
    try:
        # Write to Markdown file
        with open(md_path, "w", encoding="utf-8") as md_file:
            md_file.write(md_content)
        print(f"Markdown file saved to: {md_path}")
    except Exception as e:
        print(f"Failed to write Markdown file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Convert a PDF file to Markdown format.")
    parser.add_argument("pdf_file_path", help="Path to the PDF file to be converted.")
    args = parser.parse_args()

    convert_pdf_to_markdown(args.pdf_file_path)

if __name__ == "__main__":
    main()
