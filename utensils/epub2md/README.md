# EPUB to Markdown Converter

## Overview

This script provides a utility for converting EPUB files to Markdown format. It leverages the `ebooklib` library to read EPUB content and the `html2text` module for the conversion of HTML documents contained within the EPUB to Markdown format.

## Installation

Before running the script, ensure you have Python 3.12 installed on your system and install the required Python dependencies by running:

```Bash
pip install -r requirements.txt
```

Optional, use pyenv to manage your Python environments

```Bash
pyenv local 3.12
```

## Usage

To convert an EPUB file to Markdown:

```
./epub_to_md.py <path_to_epub_file>
```

For example:

```Bash
./epub_to_md.py example.epub
```

This will create a Markdown file in the same directory as the EPUB file, with the same name but with a `.md` extension.

## How It Works

1. **EPUB Loading**: The script reads the EPUB file using `ebooklib`.
2. **HTML to Markdown Conversion**: Each document within the EPUB is converted from HTML to Markdown format using `html2text`.
3. **Markdown File Creation**: The script combines all converted Markdown content into a single file, naming it after the original EPUB file but with a `.md` extension.

## Dependencies

- Python 3.12
- Optional pyenv to manage your Python environments
- `ebooklib`: a Python library for managing EPUB2/EPUB3 and Kindle files
- `html2text`: a Python library for the conversion of HTML into Markdown

## License

This software is released under the AGPL-3.0 license.

