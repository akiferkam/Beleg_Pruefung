"""F: Geschäftsregeln (F1-F2)."""
from __future__ import annotations

from .base import Finding, ok


def check_amount_threshold(extraction: dict, threshold_eur: float) -> Finding:
    gross = extraction.get("gross_amount")
    if gross is None:
        return ok("F1", "Kein Bruttobetrag vorhanden - Prüfung entfällt.", level="INFO")
    if gross > threshold_eur:
        return Finding(
            check_id="F1", level="BLOCK", passed=False,
            message=f"Rechnungsbetrag {gross:.2f} € überschreitet die Freigabegrenze von {threshold_eur:.2f} € - Vier-Augen-Prinzip greift immer.",
            policy_tunable=True,
        )
    return Finding(check_id="F1", level="BLOCK", passed=True, message=f"Rechnungsbetrag {gross:.2f} € unterhalb der Freigabegrenze von {threshold_eur:.2f} €.", policy_tunable=True)


def check_skonto(extraction: dict) -> Finding:
    terms = extraction.get("skonto_terms")
    if terms:
        return ok("F2", f"Skonto-Hinweis im Beleg: {terms}.", level="INFO")
    return ok("F2", "Kein Skonto-Hinweis im Beleg.", level="INFO")
