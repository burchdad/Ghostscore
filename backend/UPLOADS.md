Upload / OCR Requirements

GhostScore credit report upload supports text, CSV, and PDF reports. For best results with scanned PDFs, install the following:

- Tesseract (OCR):
  - Ubuntu/Debian: `sudo apt-get install -y tesseract-ocr`
  - macOS (Homebrew): `brew install tesseract`

- Poppler (for `pdf2image` on PDFs):
  - Ubuntu/Debian: `sudo apt-get install -y poppler-utils`
  - macOS: `brew install poppler`

Python dependencies (backend):

```sh
cd backend
python3 -m pip install -r requirements.txt
```

Notes:
- `pytesseract` requires the Tesseract binary installed on the system.
- `pdf2image` requires Poppler (or an alternate PDF rasterizer) to convert PDF pages to images.

Running parser tests:

```sh
cd backend
pytest -q
```

If OCR is not available, the parser will attempt to parse text content; scanned PDFs may require OCR to extract text.
