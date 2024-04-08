# PDF to Markdown Converter

## Overview

This script provides a utility for converting PDF files to Markdown format. It leverages the `PyMuPDF` library to convert PDF documents to the Markdown format.

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

To convert an PDF file to Markdown:

```
./pdf2md.py <path_to_PDF_file>
```

For example:

```Bash
./pdf2md.py example.pdf
```

This will create a Markdown file in the same directory as the PDF file, with the same name but with a `.md` extension.

## How It Works

1. **PDF Loading**: The script reads the PDF file using `PyMuPDF`.
2. **PDF to Markdown Conversion**: Each PDF is converted to Markdown format.
3. **Markdown File Creation**: The script combines all converted Markdown content into a single file, naming it after the original PDF file but with a `.md` extension.

## Dependencies

- Python 3.12
- Optional pyenv to manage your Python environments
- `PyMuPDF` is a versatile Python library for the manipulation, rendering, and extraction of content from PDF files

## License

This software is released under the AGPL-3.0 license.

