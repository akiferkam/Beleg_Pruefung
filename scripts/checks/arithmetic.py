"""C: Rechnerische Prüfung (C1-C6).

Bewusst robust gegen gerundete Anzeige-Einzelpreise (z.B. 0,021 € wird oft
als "0,02" angezeigt): C1 prüft mit einer Toleranz pro Einheit statt exakter
Gleichheit, sonst würden korrekte Rechnungen wie b01 fälschlich durchfallen.
"""
from __future__ import annotations

from .base import Finding, fail, ok


def check_line_arithmetic(extraction: dict, tolerance_per_unit: float) -> Finding:
    problems = []
    checked = 0
    for i, item in enumerate(extraction.get("line_items") or [], start=1):
        qty, price, total = item.get("quantity"), item.get("unit_price"), item.get("line_total")
        if qty is None or price is None or total is None:
            continue
        checked += 1
        allowed = abs(qty) * tolerance_per_unit
        diff = abs(qty * price - total)
        if diff > allowed:
            problems.append(f"Pos.{i} '{item.get('description', '')}': {qty} × {price} = {qty * price:.2f}, Rechnung sagt {total:.2f} (Differenz {diff:.2f} € > Toleranz {allowed:.2f} €)")
    if problems:
        return fail("C1", "Positions-Arithmetik stimmt nicht: " + "; ".join(problems))
    return ok("C1", f"Positions-Arithmetik korrekt ({checked} Position(en) geprüft, Toleranz {tolerance_per_unit} €/Einheit für gerundete Anzeigepreise).")


def check_net_sum(extraction: dict, tolerance: float) -> Finding:
    items = extraction.get("line_items") or []
    totals = [i.get("line_total") for i in items if i.get("line_total") is not None]
    net = extraction.get("net_amount")
    if not totals or net is None:
        return ok("C2", "Zu wenig Daten für Summenprüfung - übersprungen.", level="INFO")
    line_sum = sum(totals)
    diff = abs(line_sum - net)
    if diff > tolerance:
        return fail("C2", f"Summe der Positionen ({line_sum:.2f} €) weicht vom ausgewiesenen Nettobetrag ({net:.2f} €) ab: Differenz {diff:.2f} €.")
    return ok("C2", f"Summe der Positionen ({line_sum:.2f} €) stimmt mit Nettobetrag ({net:.2f} €) überein.")


def check_vat_rate_valid(extraction: dict, valid_rates: list[float]) -> Finding:
    rate = extraction.get("vat_rate_pct")
    if rate is None:
        return ok("C3", "Kein USt-Satz vorhanden - wird bereits unter B5 gemeldet.", level="INFO")
    if rate not in valid_rates:
        return fail("C3", f"USt-Satz {rate}% ist kein gültiger Satz ({valid_rates}).")
    return ok("C3", f"USt-Satz {rate}% ist gültig.")


def check_vat_amount(extraction: dict, tolerance: float) -> Finding:
    net, rate, vat = extraction.get("net_amount"), extraction.get("vat_rate_pct"), extraction.get("vat_amount")
    if net is None or rate is None or vat is None:
        return ok("C4", "Zu wenig Daten für USt-Berechnung - übersprungen.", level="INFO")
    expected = net * rate / 100
    diff = abs(expected - vat)
    if diff > tolerance:
        return fail("C4", f"USt-Betrag stimmt nicht: {net:.2f} € × {rate}% = {expected:.2f} €, Rechnung sagt {vat:.2f} € (Differenz {diff:.2f} €).")
    return ok("C4", f"USt-Betrag korrekt: {net:.2f} € × {rate}% = {vat:.2f} €.")


def check_gross_amount(extraction: dict, tolerance: float) -> Finding:
    net, vat, gross = extraction.get("net_amount"), extraction.get("vat_amount"), extraction.get("gross_amount")
    if net is None or vat is None or gross is None:
        return ok("C5", "Zu wenig Daten für Bruttoprüfung - übersprungen.", level="INFO")
    expected = net + vat
    diff = abs(expected - gross)
    if diff > tolerance:
        return fail("C5", f"Brutto stimmt nicht: Netto {net:.2f} € + USt {vat:.2f} € = {expected:.2f} €, Rechnung sagt {gross:.2f} € (Differenz {diff:.2f} €).")
    return ok("C5", f"Brutto korrekt: {net:.2f} € + {vat:.2f} € = {gross:.2f} €.")


def check_currency_and_positive(extraction: dict) -> Finding:
    currency = (extraction.get("currency") or "").upper()
    gross = extraction.get("gross_amount")
    if currency and currency != "EUR":
        return fail("C6", f"Währung ist {currency}, nicht EUR.")
    if gross is not None and gross <= 0:
        return fail("C6", f"Rechnungsbetrag ist nicht positiv: {gross}.")
    return ok("C6", "Währung EUR, Betrag positiv.")
