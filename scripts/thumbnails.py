"""Kleine Vorschaubilder (Thumbnails) für PDFs/Bilder - nur für die Web-UI."""
from __future__ import annotations

import hashlib
import io
import os

import pymupdf
from PIL import Image

THUMB_MAX_DIM = 320


def _cache_key(path: str) -> str:
    st = os.stat(path)
    raw = f"{os.path.abspath(path)}:{st.st_mtime_ns}:{st.st_size}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_thumbnail(path: str, cache_dir: str) -> bytes:
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, _cache_key(path) + ".png")
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return f.read()

    suffix = os.path.splitext(path)[1].lower()
    if suffix == ".pdf":
        doc = pymupdf.open(path)
        page = doc[0]
        zoom = THUMB_MAX_DIM / max(page.rect.width, page.rect.height)
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        doc.close()
    else:
        img = Image.open(path).convert("RGB")

    img.thumbnail((THUMB_MAX_DIM, THUMB_MAX_DIM))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    data = buf.getvalue()
    with open(cache_path, "wb") as f:
        f.write(data)
    return data
