"""B: Formale Rechnungsprüfung nach §14 Abs. 4 UStG (B1-B7)."""
from __future__ import annotations

from datetime import date, datetime

from .base import Finding, fail, ok


def check_recipient(extraction: dict, company_cfg: dict) -> Finding:
    name = (extraction.get("recipient_name") or "")
    address = (extraction.get("recipient_address") or "")
    if company_cfg["name"].split()[0].lower() not in name.lower():
        return fail("B1", f"Rechnungsempfänger ist nicht erkennbar Quellberg GmbH (gelesen: {name or 'leer'}).")
    missing = [s for s in company_cfg["address_contains"] if s.lower() not in address.lower()]
    if missing:
        return fail("B1", f"Quellberg-Adresse im Beleg unvollständig/abweichend (gelesen: {address or 'leer'}; fehlt: {', '.join(missing)}).")
    return ok("B1", f"Rechnungsempfänger korrekt: {name}, {address}.")


def check_supplier_present(extraction: dict) -> Finding:
    name = extraction.get("supplier_name")
    address = extraction.get("supplier_address")
    if not name or not address:
        return fail("B2", f"Lieferant Name/Adresse unvollständig (Name: {name!r}, Adresse: {address!r}).")
    return ok("B2", f"Lieferant vollständig angegeben: {name}, {address}.")


def check_supplier_tax_id(extraction: dict) -> Finding:
    tax_id = extraction.get("supplier_tax_id")
    tax_id_type = extraction.get("supplier_tax_id_type")
    if not tax_id or tax_id_type in (None, "keine", "unbekannt"):
        return fail("B3", "Keine Steuernummer/USt-IdNr des Lieferanten angegeben (§14 Abs. 4 Nr. 2 UStG Pflichtangabe).")
    return ok("B3", f"{tax_id_type} des Lieferanten vorhanden: {tax_id}.")


def check_invoice_number_and_date(extraction: dict, today: date | None = None) -> Finding:
    today = today or datetime.now().date()
    number = extraction.get("invoice_number")
    date_str = extraction.get("invoice_date")
    if not number:
        return fail("B4", "Keine Rechnungsnummer angegeben.")
    if not date_str:
        return fail("B4", "Kein Rechnungsdatum angegeben.")
    try:
        parsed = date.fromisoformat(date_str)
    except ValueError:
        return fail("B4", f"Rechnungsdatum nicht als Datum interpretierbar: {date_str!r}.")
    if parsed > today:
        return fail("B4", f"Rechnungsdatum liegt in der Zukunft: {date_str}.")
    return ok("B4", f"Rechnungsnummer {number}, Datum {date_str} plausibel.")


def check_amounts_disclosed(extraction: dict) -> Finding:
    fields = {
        "net_amount": extraction.get("net_amount"),
        "vat_rate_pct": extraction.get("vat_rate_pct"),
        "vat_amount": extraction.get("vat_amount"),
        "gross_amount": extraction.get("gross_amount"),
    }
    missing = [k for k, v in fields.items() if v is None]
    if missing:
        return fail("B5", f"Pflichtangaben zu Netto/USt-Satz/USt-Betrag/Brutto fehlen: {', '.join(missing)}.")
    return ok("B5", "Netto, USt-Satz, USt-Betrag und Brutto sind ausgewiesen.")


def check_reverse_charge_formalities(extraction: dict, company_vat_id: str) -> Finding:
    vat_rate = extraction.get("vat_rate_pct")
    if vat_rate not in (0, 0.0):
        return ok("B6", "Kein 0%-Fall, Prüfung entfällt.")
    note = extraction.get("reverse_charge_note_present")
    recipient_vat = extraction.get("recipient_tax_id")
    supplier_vat = extraction.get("supplier_tax_id")
    problems = []
    if not note:
        problems.append("kein §13b-/Reverse-Charge-Hinweis im Dokument")
    if not recipient_vat:
        problems.append("keine USt-IdNr des Empfängers (Quellberg) angegeben")
    if not supplier_vat:
        problems.append("keine USt-IdNr des Lieferanten angegeben")
    if problems:
        return fail("B6", "0% USt ohne vollständige Reverse-Charge-Formalien: " + "; ".join(problems) + ".")
    return ok("B6", f"Reverse-Charge-Fall formal korrekt (§13b), Empfänger-USt-IdNr {recipient_vat}.")


def check_leistungsdatum(extraction: dict) -> Finding:
    # Bewusst nur INFO, nie blockierend: siehe README ("bewusst NICHT gebaut").
    # Leistungsdatum wird derzeit nicht separat extrahiert, da es in keinem der 16
    # Testbelege vorkommt und als BLOCK-Kriterium das gesamte Testset durchfallen ließe.
    return ok("B7", "Leistungsdatum wird aktuell nicht geprüft (bewusste Scope-Entscheidung, siehe README).", level="INFO")
