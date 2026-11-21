
import os
import tempfile

from flask import Flask, request, Response
from pypdf import PdfReader

try:
    import pymupdf
except ImportError:
    import fitz as pymupdf

from rapidocr_onnxruntime import RapidOCR

app = Flask(__name__)

# OCR engine
engine = RapidOCR()


def ocr_page(doc, page_index):
    png = doc[page_index].get_pixmap(dpi=200).tobytes("png")
    result, _ = engine(png)

    if not result:
        return ""

    items = []

    for box, text, score in result:
        ys = [p[1] for p in box]
        xs = [p[0] for p in box]
        items.append((min(ys), max(ys), min(xs), text))

    items.sort(key=lambda x: (x[0], x[2]))

    lines = []
    current = []
    last_mid = None
    last_h = None

    for top, bottom, left, text in items:
        mid = (top + bottom) / 2
        height = bottom - top

        if (
            last_mid is not None
            and abs(mid - last_mid) > max(last_h, height) * 0.6
        ):
            lines.append(current)
            current = []

        current.append((left, text))
        last_mid = mid
        last_h = height

    if current:
        lines.append(current)

    return "\n".join(
        " ".join(text for _, text in sorted(line))
        for line in lines
    )


@app.route("/", methods=["GET"])
def home():
    return "Invoice OCR API is running", 200


@app.route("/invoice", methods=["GET", "POST"])
def invoice():

    if request.method == "GET":
        return "Invoice OCR API is ready. Send PDF using POST.", 200

    uploaded_file = request.files.get("file")

    if uploaded_file is None or not uploaded_file.filename:
        return Response(
            "PDF file missing. Use form-data key 'file'.",
            status=400
        )

    if not uploaded_file.filename.lower().endswith(".pdf"):
        return Response("Only PDF files are allowed.", status=400)

    temp_path = None
    doc = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
            dir="/tmp"
        ) as temp:
            uploaded_file.save(temp)
            temp_path = temp.name

        reader = PdfReader(temp_path, strict=False)

        if reader.is_encrypted:
            return Response(
                "Encrypted PDF is not supported.",
                status=400
            )

        doc = pymupdf.open(temp_path)
        extracted_pages = []

        for i, page in enumerate(reader.pages):
            # Extract existing PDF text first
            text = (page.extract_text() or "").strip()

            # If no text exists, use OCR
            if not text:
                text = ocr_page(doc, i).strip()

            if text:
                extracted_pages.append(text)

        return Response(
            "\n\n".join(extracted_pages),
            mimetype="text/plain"
        )

    except Exception:
        app.logger.exception("PDF extraction failed")
        return Response(
            "PDF processing failed. Check Vercel runtime logs.",
            status=500
        )

    finally:
        if doc is not None:
            doc.close()

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
