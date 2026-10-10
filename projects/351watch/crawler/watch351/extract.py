"""Generic document -> plain text extraction (PDF, HTML, DOCX).

PDFs go through poppler's `pdftotext` (reading-order mode, which keeps agenda
items on their own lines better than -layout for multi-column headers).
A PDF that yields almost no text is flagged `scanned=True` (an image from a
copier). If the `tesseract` binary is installed, the first OCR_MAX_PAGES pages
are OCR'd instead (pdftoppm -> tesseract) and the result is cached by content
hash, so re-runs do not repeat the slow step. Without tesseract, scans are
counted and skipped.
"""

from __future__ import annotations

import hashlib
import io
import os
import re
import shutil
import subprocess
import tempfile
import threading
import zipfile
from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup

from .fetch import DEFAULT_CACHE_DIR, Response

OCR_MAX_PAGES = 12          # agenda packets: the agenda itself is up front
OCR_CACHE = DEFAULT_CACHE_DIR / "ocr"
TESSERACT = shutil.which("tesseract")
# OCR is CPU-bound: run one single-threaded tesseract per core, no matter how
# many towns are being crawled in parallel.
_OCR_SLOTS = threading.Semaphore(max(1, (os.cpu_count() or 2) - 1))
_OCR_ENV = {**os.environ, "OMP_THREAD_LIMIT": "1"}


@dataclass
class Extracted:
    text: str
    kind: str          # "pdf" | "html" | "docx" | "unsupported"
    pages: int = 0
    scanned: bool = False   # no text layer (image-only PDF)
    ocr: bool = False       # text came from OCR
    error: str | None = None


def _pdf_pages(path: str) -> int:
    try:
        out = subprocess.run(["pdfinfo", path], capture_output=True, text=True, timeout=30).stdout
        m = re.search(r"^Pages:\s+(\d+)", out, re.M)
        return int(m.group(1)) if m else 0
    except (subprocess.SubprocessError, OSError):
        return 0


def pdf_to_text(data: bytes) -> Extracted:
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        tmp.write(data)
        tmp.flush()
        pages = _pdf_pages(tmp.name)
        try:
            proc = subprocess.run(["pdftotext", "-enc", "UTF-8", "-q", tmp.name, "-"],
                                  capture_output=True, timeout=120)
        except subprocess.TimeoutExpired:
            return Extracted("", "pdf", pages, error="pdftotext timeout")
    text = proc.stdout.decode("utf-8", errors="replace")
    visible = len(re.sub(r"\s+", "", text))
    scanned = visible < max(80, 25 * max(pages, 1))
    error = None if proc.returncode == 0 else f"pdftotext exit {proc.returncode}"
    if scanned and TESSERACT:
        ocr_text = ocr_pdf(data)
        if ocr_text.strip():
            return Extracted(ocr_text, "pdf", pages, scanned=True, ocr=True)
    return Extracted(text, "pdf", pages, scanned=scanned, error=error)


def ocr_pdf(data: bytes) -> str:
    """Rasterize the first OCR_MAX_PAGES pages at 200 dpi and OCR them."""
    key = hashlib.sha256(data).hexdigest()[:32]
    cached = OCR_CACHE / f"{key}.txt"
    if cached.exists():
        return cached.read_text()
    with _OCR_SLOTS, tempfile.TemporaryDirectory() as tmp:
        pdf = Path(tmp) / "in.pdf"
        pdf.write_bytes(data)
        try:
            subprocess.run(["pdftoppm", "-r", "200", "-gray", "-png", "-f", "1",
                            "-l", str(OCR_MAX_PAGES), str(pdf), str(Path(tmp) / "p")],
                           capture_output=True, timeout=300, check=True)
            parts = []
            for png in sorted(Path(tmp).glob("p-*.png")):
                out = subprocess.run([TESSERACT, str(png), "-", "--psm", "3"],
                                     capture_output=True, timeout=180, env=_OCR_ENV)
                parts.append(out.stdout.decode("utf-8", errors="replace"))
        except (subprocess.SubprocessError, OSError):
            return ""
    text = "\n".join(parts)
    OCR_CACHE.mkdir(parents=True, exist_ok=True)
    cached.write_text(text)
    return text


def html_to_text(html: str) -> Extracted:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "nav", "header", "footer", "form", "svg"]):
        tag.decompose()
    main = soup.find("main") or soup.find(id=re.compile("content|main", re.I)) or soup.body or soup
    text = main.get_text("\n", strip=True)
    if len(text) < 200:
        # Nearly empty: the id match was a tiny element (a "skip to main content" link) or the
        # whole page sits inside an ASP.NET <form> (Legistar). Re-read the body keeping forms.
        soup2 = BeautifulSoup(html, "lxml")
        for tag in soup2(["script", "style", "noscript", "svg"]):
            tag.decompose()
        body = soup2.body or soup2
        alt = body.get_text("\n", strip=True)
        if len(alt) > len(text):
            text = alt
    return Extracted(text, "html")


def docx_to_text(data: bytes) -> Extracted:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            xml = z.read("word/document.xml").decode("utf-8", errors="replace")
    except (zipfile.BadZipFile, KeyError) as e:
        return Extracted("", "docx", error=str(e))
    xml = re.sub(r"</w:p>", "\n", xml)
    text = re.sub(r"<[^>]+>", "", xml)
    return Extracted(text, "docx")


def extract(resp: Response) -> Extracted:
    ctype = resp.content_type.lower()
    if resp.is_pdf:
        return pdf_to_text(resp.body)
    if "wordprocessingml" in ctype or resp.final_url.lower().split("?")[0].endswith(".docx"):
        return docx_to_text(resp.body)
    if "html" in ctype or resp.body.lstrip()[:1] == b"<":
        return html_to_text(resp.text)
    if ctype.startswith("text/"):
        return Extracted(resp.text, "text")
    return Extracted("", "unsupported", error=f"content-type {ctype or 'unknown'}")
