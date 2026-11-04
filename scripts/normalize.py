"""
Normalisierung + Grounding (Katalog-Check A5).

Grounding = Schutz gegen Halluzination: jeder vom Modell extrahierte Betrag
muss sich - in irgendeiner üblichen Zahlenschreibweise (de: 1.500,00 /
en: 1,500.00 / ohne Tausendertrennzeichen) - im tatsächlichen Rohtext des
Belegs wiederfinden. Findet er sich nicht, ist das ein Hinweis, dass das
Modell etwas erfunden oder falsch gelesen hat, und der Beleg fällt auf
hinschauen (nicht: der Fehler wird stillschweigend ignoriert).

Bei Fotos ohne digitale Textschicht ist Grounding nicht möglich - das wird
explizit als "übersprungen", nicht als "fehlgeschlagen" markiert.
"""
from __future__ import annotations

from dataclasses import dataclass, field

_STRIP_CHARS = [" ", "\n", "\t", "\r", "\xa0", "€", "$", "£", "EUR", "eur"]


def squash(text: str) -> str:
    t = text
    for ch in _STRIP_CHARS:
        t = t.replace(ch, "")
    return t.lower()


def to_de(value: float, decimals: int = 2) -> str:
    s = f"{value:,.{decimals}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def to_en(value: float, decimals: int = 2) -> str:
    return f"{value:,.{decimals}f}"


def to_plain(value: float, decimals: int = 2) -> str:
    return f"{value:.{decimals}f}"


def amount_candidates(value: float) -> set[str]:
    """Alle plausiblen textuellen Schreibweisen eines Betrags/einer Menge."""
    candidates: set[str] = set()
    for decimals in (2, 0):
        try:
            candidates.add(to_de(value, decimals))
            candidates.add(to_en(value, decimals))
            candidates.add(to_plain(value, decimals))
        except (ValueError, OverflowError):
            continue
    # Varianten ohne Nachkommastellen zusätzlich ohne führende Null-Nachkommastellen
    if float(value).is_integer():
        candidates.add(str(int(value)))
    return {c for c in candidates if c}


def is_grounded(value: float | int | None, squashed_text: str) -> bool | None:
    """True/False, oder None wenn der Wert zu trivial ist, um sinnvoll geprüft zu werden."""
    if value is None:
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    # Einstellige Ganzzahlen (z.B. Menge "2") sind im Rohtext oft ohne Dezimalstellen
    # notiert und erzeugen sonst falsche "nicht gegrounded"-Treffer, obwohl der Wert
    # korrekt ist - und als Suchmuster sind sie ohnehin zu unspezifisch. Nicht werten.
    if value.is_integer() and abs(value) < 10:
        return None
    candidates = amount_candidates(value)
    if not candidates:
        return None
    return any(squash(c) in squashed_text for c in candidates)


@dataclass
class GroundingReport:
    skipped: bool = False
    skip_reason: str | None = None
    checked_fields: list[str] = field(default_factory=list)
    ungrounded_fields: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.skipped or not self.ungrounded_fields


def check_grounding(extraction: dict, raw_text: str) -> GroundingReport:
    if not raw_text or not raw_text.strip():
        return GroundingReport(skipped=True, skip_reason="Keine digitale Textschicht (Foto/Scan ohne Textschicht).")

    squashed = squash(raw_text)
    report = GroundingReport()

    top_level_fields = ["net_amount", "vat_amount", "gross_amount"]
    for fname in top_level_fields:
        result = is_grounded(extraction.get(fname), squashed)
        if result is None:
            continue
        report.checked_fields.append(fname)
        if not result:
            report.ungrounded_fields.append(fname)

    for i, item in enumerate(extraction.get("line_items") or []):
        for sub in ("quantity", "line_total"):
            result = is_grounded(item.get(sub), squashed)
            if result is None:
                continue
            fname = f"line_items[{i}].{sub}"
            report.checked_fields.append(fname)
            if not result:
                report.ungrounded_fields.append(fname)

    return report


def normalize_iban(value: str | None) -> str | None:
    if not value:
        return None
    return value.replace(" ", "").upper()


def normalize_tax_id(value: str | None) -> str | None:
    if not value:
        return None
    return value.replace(" ", "").upper()
