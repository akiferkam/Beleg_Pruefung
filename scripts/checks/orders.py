"""D: Abgleich mit bestellungen.csv (D1-D7).

Enthält auch die Logik, welche Rechnungspositionen überhaupt "zur Bestellung
gehören" (Fuzzy-Match auf die Artikelbezeichnung) - getrennt von Positionen,
die zusätzlich und nicht bestellt in Rechnung gestellt wurden (D6).
"""
from __future__ import annotations

from rapidfuzz import fuzz

from .base import Finding, fail, ok
from po import PurchaseOrder

MATCH_THRESHOLD = 40  # Fuzzy-Score (0-100), ab dem eine Position als "zur Bestellung gehörig" zählt


def split_matched_items(line_items: list[dict], po_artikel: str) -> tuple[list[dict], list[dict]]:
    matched, extra = [], []
    for item in line_items:
        score = fuzz.token_set_ratio((item.get("description") or ""), po_artikel)
        (matched if score >= MATCH_THRESHOLD else extra).append(item)
    return matched, extra


def check_order_reference_present(extraction: dict, policy_blocks: bool) -> Finding:
    ref = extraction.get("order_reference")
    if ref:
        return ok("D1", f"Bestellnummer im Beleg angegeben: {ref}.")
    level = "BLOCK" if policy_blocks else "INFO"
    msg = "Keine Bestellnummer im Beleg - ohne Bestellbezug kann nicht geprüft werden, ob Ware/Leistung je bestellt wurde."
    return Finding(check_id="D1", level=level, passed=not policy_blocks, message=msg, policy_tunable=True)


def check_order_exists(extraction: dict, orders: dict[str, PurchaseOrder]) -> tuple[Finding, PurchaseOrder | None]:
    ref = extraction.get("order_reference")
    if not ref:
        return ok("D2", "Keine Bestellnummer angegeben - Prüfung entfällt (siehe D1).", level="INFO"), None
    po = orders.get(ref.strip())
    if po is None:
        return fail("D2", f"Bestellnummer {ref} ist nicht in bestellungen.csv bekannt."), None
    return ok("D2", f"Bestellnummer {ref} in bestellungen.csv gefunden ({po.lieferant}, {po.artikel})."), po


def check_supplier_matches_order(extraction: dict, po: PurchaseOrder, min_score: float) -> Finding:
    supplier = extraction.get("supplier_name") or ""
    score = fuzz.token_set_ratio(supplier, po.lieferant)
    if score < min_score:
        return fail("D3", f"Lieferant '{supplier}' passt nicht zu Bestellung {po.bestellnummer} ('{po.lieferant}', Ähnlichkeit {score:.0f}%).")
    return ok("D3", f"Lieferant passt zur Bestellung ({score:.0f}% Ähnlichkeit).")


def check_unit_price(extraction: dict, po: PurchaseOrder, matched_items: list[dict], tolerance_per_unit: float) -> Finding:
    if po.is_rahmenvertrag:
        return ok("D4", "Rahmenvertrag ohne festen Stückpreis - Prüfung entfällt (siehe D7).", level="INFO")
    priced = [i for i in matched_items if i.get("unit_price") is not None]
    if not priced:
        return ok("D4", "Keine passende Position mit Einzelpreis gefunden - Prüfung übersprungen.", level="INFO")
    bad = [
        i for i in priced
        if abs(i["unit_price"] - po.einzelpreis_netto) > tolerance_per_unit
    ]
    if bad:
        details = "; ".join(f"'{i.get('description', '')}': {i['unit_price']} € statt {po.einzelpreis_netto} €" for i in bad)
        return fail("D4", f"Einzelpreis weicht vom Bestellpreis ab: {details}.")
    return ok("D4", f"Einzelpreis(e) stimmen mit Bestellpreis {po.einzelpreis_netto} € überein.")


def check_cumulative_quantity(extraction: dict, po: PurchaseOrder, matched_items: list[dict], ledger, tolerance_qty: float = 1e-6) -> Finding:
    if po.is_rahmenvertrag:
        return ok("D5", "Rahmenvertrag ohne feste Menge - Prüfung entfällt (siehe D7).", level="INFO")
    this_doc_qty = sum((i.get("quantity") or 0) for i in matched_items)
    prior_qty = ledger.cumulative_quantity_for_order(po.bestellnummer, exclude_invoice_number=extraction.get("invoice_number"))
    cumulative = prior_qty + this_doc_qty
    if cumulative > po.menge + tolerance_qty:
        over = cumulative - po.menge
        over_value = over * po.einzelpreis_netto
        prior_note = f" (davon {prior_qty:g} bereits aus früheren Rechnungen zu dieser Bestellung)" if prior_qty else ""
        return fail(
            "D5",
            f"Kumulativ in Rechnung gestellte Menge ({cumulative:g}{prior_note}) übersteigt bestellte Menge "
            f"({po.menge:g}) um {over:g} Einheiten (≈ {over_value:.2f} € zu viel).",
        )
    return ok("D5", f"Kumulativ in Rechnung gestellte Menge ({cumulative:g}) liegt innerhalb der bestellten Menge ({po.menge:g}).")


def check_extra_items(extraction: dict, po: PurchaseOrder, extra_items: list[dict], tolerance_pct: float) -> Finding:
    ordered_value = po.menge * po.einzelpreis_netto
    extra_value = sum((i.get("line_total") or 0) for i in extra_items)
    if extra_value <= 0:
        return ok("D6", "Keine zusätzlichen, nicht bestellten Positionen.")
    if ordered_value <= 0:
        return fail("D6", f"Zusätzliche nicht bestellte Positionen im Wert von {extra_value:.2f} € bei einem Rahmenvertrag ohne Referenzwert - manuell prüfen.")
    pct = extra_value / ordered_value * 100
    names = ", ".join(f"'{i.get('description', '')}' ({i.get('line_total', 0):.2f} €)" for i in extra_items)
    msg = f"Zusätzliche, nicht bestellte Positionen: {names} - zusammen {extra_value:.2f} € ({pct:.1f}% des Bestellwerts {ordered_value:.2f} €)."
    if pct > tolerance_pct:
        return Finding(check_id="D6", level="BLOCK", passed=False, message=msg + f" Über der Toleranz von {tolerance_pct}%.", policy_tunable=True)
    return Finding(check_id="D6", level="BLOCK", passed=True, message=msg + f" Innerhalb der Toleranz von {tolerance_pct}%.", policy_tunable=True)


def check_rahmenvertrag_info(po: PurchaseOrder | None) -> Finding:
    if po is not None and po.is_rahmenvertrag:
        return ok("D7", f"Bestellung {po.bestellnummer} ist ein Rahmenvertrag (Einzelpreis 0) - es wird nur der Lieferantenabgleich geprüft, kein Stückpreis-/Mengenvergleich.", level="INFO")
    return ok("D7", "Keine Rahmenbestellung.", level="INFO")
