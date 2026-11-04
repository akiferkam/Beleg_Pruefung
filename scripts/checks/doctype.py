"""A3: Belegtyp muss Rechnung sein, bevor inhaltliche Prüfungen überhaupt sinnvoll sind."""
from __future__ import annotations

from .base import Finding, fail, ok

INVOICE_TYPE = "Rechnung"


def check_is_invoice(extraction: dict) -> Finding:
    doc_type = extraction.get("document_type")
    if doc_type == INVOICE_TYPE:
        return ok("A3", "Belegtyp: Rechnung.")
    statement = extraction.get("non_invoice_statement")
    extra = f" Im Dokument: „{statement}“." if statement else ""
    return fail("A3", f"Beleg ist keine Rechnung, sondern: {doc_type}.{extra} Keine Zahlungsfreigabe ohne Rechnung möglich.")
