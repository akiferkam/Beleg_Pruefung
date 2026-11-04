"""E: Betrugs- & Duplikatserkennung (E1-E6)."""
from __future__ import annotations

from .base import Finding, fail, ok
from normalize import normalize_iban


def iban_checksum_valid(iban: str) -> bool:
    iban = normalize_iban(iban) or ""
    if len(iban) < 15 or not iban[:2].isalpha() or not iban[2:4].isdigit():
        return False
    rearranged = iban[4:] + iban[:4]
    try:
        digits = "".join(str(int(ch, 36)) for ch in rearranged)
        return int(digits) % 97 == 1
    except ValueError:
        return False


def check_file_hash_duplicate(file_hash: str, ledger) -> Finding:
    prev = ledger.find_by_file_hash(file_hash)
    if prev:
        return fail("E1", f"Identische Datei wurde bereits verarbeitet (Beleg {prev.doc_id}, Rechnungsnr. {prev.invoice_number}).")
    return ok("E1", "Datei-Hash wurde noch nicht verarbeitet.")


def check_invoice_number_duplicate(extraction: dict, ledger) -> Finding:
    prev = ledger.find_by_supplier_and_invoice_number(extraction.get("supplier_name"), extraction.get("invoice_number"))
    if prev:
        return fail("E2", f"Gleicher Lieferant + gleiche Rechnungsnummer bereits verarbeitet (Beleg {prev.doc_id}).")
    return ok("E2", "Keine Dopplung von Lieferant + Rechnungsnummer im Ledger.")


def check_content_duplicate(extraction: dict, fingerprint: str, ledger) -> Finding:
    prev = ledger.find_content_duplicate(fingerprint, extraction.get("gross_amount"), extraction.get("invoice_number"))
    if prev:
        return fail(
            "E3",
            f"Inhaltliches Duplikat: identische Positionen/Beträge wie bereits verarbeiteter Beleg {prev.doc_id} "
            f"(Rechnungsnr. {prev.invoice_number}), hier aber unter neuer Rechnungsnummer "
            f"{extraction.get('invoice_number')} - vermutlich dieselbe Leistung erneut in Rechnung gestellt.",
        )
    return ok("E3", "Kein inhaltliches Duplikat im Ledger gefunden.")


def check_iban_checksum(extraction: dict) -> Finding:
    iban = extraction.get("supplier_iban")
    if not iban:
        return ok("E4", "Keine IBAN im Beleg angegeben - Prüfung entfällt.", level="INFO")
    if not iban_checksum_valid(iban):
        return fail("E4", f"IBAN-Prüfsumme ungültig: {iban}.")
    return ok("E4", f"IBAN-Prüfsumme gültig: {iban}.")


def check_iban_matches_history(extraction: dict, ledger) -> Finding:
    iban = normalize_iban(extraction.get("supplier_iban"))
    if not iban:
        return ok("E5", "Keine IBAN im Beleg angegeben - Prüfung entfällt.", level="INFO")
    previous = ledger.previous_ibans_for_supplier(extraction.get("supplier_name"))
    if not previous:
        return ok("E5", "Erste bekannte Rechnung dieses Lieferanten - keine Historie zum Abgleich.", level="INFO")
    if iban not in previous and previous:
        return fail("E5", f"IBAN weicht von früher für diesen Lieferanten verwendeter IBAN ab (neu: {iban}, bisher: {', '.join(previous)}) - mögliche Kontoänderung/Betrugsversuch.")
    return ok("E5", "IBAN stimmt mit bisheriger Historie dieses Lieferanten überein.")


def check_manipulation_attempt(extraction: dict) -> Finding:
    attempt = extraction.get("manipulation_attempt")
    if attempt:
        return fail("E6", f"Im Dokument wurde eine an ein Prüfsystem/eine KI gerichtete Formulierung gefunden und ignoriert: „{attempt}“.")
    return ok("E6", "Keine an ein Prüfsystem gerichtete Formulierung im Dokument gefunden.")
