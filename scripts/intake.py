"""
Intake: beliebiges Belegformat -> einheitliche interne Repräsentation
(Seitenbilder als PNG-Bytes + Textschicht, falls vorhanden).

Alles, was hier nicht gelesen werden kann, wird als nicht-lesbar markiert
und fällt in der Decision-Stufe automatisch auf hinschauen (Check A1/A2) -
es wird nie stillschweigend übersprungen.
"""
from __future__ import annotations

import io
from dataclasses import dataclass, field

import pymupdf
from PIL import Image

RENDER_DPI = 200
MAX_IMAGE_DIM = 1600  # Downscale sehr großer Fotos, damit die Vision-API sie zuverlässig verarbeitet

SUPPORTED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".heic"}
SUPPORTED_PDF_SUFFIXES = {".pdf"}


@dataclass
class PageContent:
    image_png: bytes
    text: str


@dataclass
class IntakeResult:
    doc_id: str
    file_path: str
    file_type: str
    pages: list[PageContent] = field(default_factory=list)
    readable: bool = True
    error: str | None = None

    @property
    def combined_text(self) -> str:
        return "\n".join(p.text for p in self.pages if p.text)

    @property
    def page_count(self) -> int:
        return len(self.pages)


def _resize_if_needed(img: Image.Image) -> Image.Image:
    w, h = img.size
    longest = max(w, h)
    if longest <= MAX_IMAGE_DIM:
        return img
    scale = MAX_IMAGE_DIM / longest
    return img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)


def _pil_to_png_bytes(img: Image.Image) -> bytes:
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def load_document(path: str) -> IntakeResult:
    import os

    doc_id = os.path.splitext(os.path.basename(path))[0]
    suffix = os.path.splitext(path)[1].lower()

    if suffix in SUPPORTED_PDF_SUFFIXES:
        return _load_pdf(doc_id, path)
    if suffix in SUPPORTED_IMAGE_SUFFIXES:
        return _load_image(doc_id, path, suffix)

    return IntakeResult(
        doc_id=doc_id,
        file_path=path,
        file_type=suffix or "unbekannt",
        readable=False,
        error=f"Nicht unterstütztes Dateiformat: {suffix!r}",
    )


def _load_pdf(doc_id: str, path: str) -> IntakeResult:
    try:
        doc = pymupdf.open(path)
    except Exception as exc:  # beschädigt, verschlüsselt, kein gültiges PDF...
        return IntakeResult(
            doc_id=doc_id, file_path=path, file_type="pdf",
            readable=False, error=f"PDF konnte nicht geöffnet werden: {exc}",
        )

    if doc.is_encrypted:
        ok = doc.authenticate("")  # leeres Passwort versuchen, sonst unlesbar
        if not ok:
            return IntakeResult(
                doc_id=doc_id, file_path=path, file_type="pdf",
                readable=False, error="PDF ist passwortgeschützt.",
            )

    pages: list[PageContent] = []
    try:
        for page in doc:
            text = page.get_text()
            pix = page.get_pixmap(dpi=RENDER_DPI)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            img = _resize_if_needed(img)
            pages.append(PageContent(image_png=_pil_to_png_bytes(img), text=text))
    except Exception as exc:
        return IntakeResult(
            doc_id=doc_id, file_path=path, file_type="pdf",
            readable=False, error=f"Fehler beim Rendern der Seiten: {exc}",
        )

    if not pages:
        return IntakeResult(
            doc_id=doc_id, file_path=path, file_type="pdf",
            readable=False, error="PDF enthält keine Seiten.",
        )

    return IntakeResult(doc_id=doc_id, file_path=path, file_type="pdf", pages=pages)


def _load_image(doc_id: str, path: str, suffix: str) -> IntakeResult:
    try:
        img = Image.open(path)
        img.load()
    except Exception as exc:
        return IntakeResult(
            doc_id=doc_id, file_path=path, file_type=suffix.lstrip("."),
            readable=False, error=f"Bild konnte nicht geöffnet werden: {exc}",
        )

    img = _resize_if_needed(img)
    # Fotos haben keine Textschicht - Grounding (A5) wird dafür bewusst übersprungen,
    # nicht fälschlich als Halluzination gewertet.
    page = PageContent(image_png=_pil_to_png_bytes(img), text="")
    return IntakeResult(doc_id=doc_id, file_path=path, file_type=suffix.lstrip("."), pages=[page])
