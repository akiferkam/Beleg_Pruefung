"""A: Lesbarkeit & Format (A1, A2, A4, A5)."""
from __future__ import annotations

from .base import Finding, fail, ok


def check_file_readable(intake_result) -> Finding:
    if intake_result.readable:
        return ok("A1", "Datei konnte geöffnet und gelesen werden.")
    return fail("A1", f"Datei konnte nicht gelesen werden: {intake_result.error}")


def check_fields_readable(extraction: dict | None, extraction_error: str | None) -> Finding:
    if extraction_error:
        return fail("A2", f"Extraktion fehlgeschlagen: {extraction_error}")
    if extraction is None:
        return fail("A2", "Keine Extraktion verfügbar.")
    if extraction.get("unreadable_or_incomplete"):
        reason = extraction.get("unreadable_reason") or "kein Grund angegeben"
        return fail("A2", f"Kernfelder laut Modell nicht zuverlässig lesbar: {reason}")
    return ok("A2", "Kernfelder (Beträge, Lieferant, Rechnungsnummer) wurden lesbar extrahiert.")


def check_pages_complete(intake_result, extraction: dict) -> Finding:
    stated = extraction.get("pages_stated_total")
    actual = intake_result.page_count
    if stated is None:
        return ok("A4", "Keine Seitenangabe im Dokument (z.B. 'Seite 1 von N') - Prüfung entfällt.")
    if stated != actual:
        return fail("A4", f"Dokument gibt {stated} Seite(n) an, es wurden aber {actual} Seite(n) geliefert - Beleg vermutlich unvollständig.")
    return ok("A4", f"Seitenzahl stimmt ({actual}/{stated}).")


def check_grounding(grounding_report) -> Finding:
    if grounding_report.skipped:
        return ok("A5", f"Grounding übersprungen: {grounding_report.skip_reason}")
    if grounding_report.passed:
        return ok("A5", f"Alle geprüften Beträge/Mengen ({len(grounding_report.checked_fields)}) im Rohtext wiedergefunden.")
    return fail(
        "A5",
        "Mögliche Halluzination: folgende extrahierte Werte wurden im Rohtext/Textschicht NICHT wiedergefunden: "
        + ", ".join(grounding_report.ungrounded_fields),
    )
