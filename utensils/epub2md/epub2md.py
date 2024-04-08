#!/usr/bin/env python3

import sys
import os
import argparse
import ebooklib
from ebooklib import epub
import html2text

def convert_html_to_markdown(html_content):
    # Initialize html2text
    h = html2text.HTML2Text()
    h.ignore_links = False
    return h.handle(html_content)

def epub_to_md(epub_path):
    try:
        # Load the EPUB file
        book = epub.read_epub(epub_path)
    except Exception as e:
        print(f"Failed to read EPUB file: {e}")
        return

    # Initialize Markdown content
    md_content = ""

    # check each item in the EPUB book
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        # Convert HTML to Markdown
        html_content = item.content.decode("utf-8")
        md_content += convert_html_to_markdown(html_content) + "\n\n"


    if not md_content:
        print("No readable document items found in the EPUB file.")
        return

    # Generate output file path
    md_path = os.path.splitext(epub_path)[0] + ".md"
    
    try:
        # Write to Markdown file
        with open(md_path, "w", encoding="utf-8") as md_file:
            md_file.write(md_content)
        print(f"Markdown file saved to: {md_path}")
    except Exception as e:
        print(f"Failed to write Markdown file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Convert an EPUB file to Markdown format.")
    parser.add_argument("epub_file_path", help="Path to the EPUB file to be converted.")
    args = parser.parse_args()

    epub_to_md(args.epub_file_path)

if __name__ == "__main__":
    main()
