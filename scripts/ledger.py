"""
Ledger: lauf-übergreifendes Gedächtnis vergangener Rechnungen.

Warum das nötig ist: ein Duplikat erkennt man nicht an der Rechnungsnummer
(die kann sich ändern, siehe b10 als Kopie von b06 mit neuer Nummer/Vorlage).
Generisch funktioniert das nur über "was wurde zu dieser Bestellung bereits
kumuliert in Rechnung gestellt" + "gab es inhaltlich schon eine (fast)
identische Rechnung". Das muss über einzelne Skill-Läufe hinweg gespeichert
werden, weil eine doppelte Rechnung in der Praxis auch Wochen später
eintreffen kann.

Das Ledger wird NICHT während eines Laufs für alle Belege auf einmal
geschrieben, sondern Beleg für Beleg (in Rechnungsdatum-Reihenfolge) -
siehe run.py. So sieht Beleg N bereits alle vorher verarbeiteten Belege,
exakt wie im Wirkbetrieb.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def line_items_fingerprint(line_items: list[dict]) -> str:
    """Inhaltlicher Fingerabdruck unabhängig von Rechnungsnummer/Vorlage/Reihenfolge."""
    normalized = sorted(
        (
            (item.get("description") or "").strip().lower(),
            round(float(item.get("quantity") or 0), 4),
            round(float(item.get("unit_price") or 0), 4),
            round(float(item.get("line_total") or 0), 2),
        )
        for item in (line_items or [])
    )
    raw = json.dumps(normalized, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass
class LedgerEntry:
    doc_id: str
    file_hash: str
    supplier_name: str | None
    invoice_number: str | None
    invoice_date: str | None
    order_reference: str | None
    net_amount: float | None
    gross_amount: float | None
    total_quantity: float | None
    line_items_fp: str
    supplier_iban: str | None
    decision: str | None = None
    processed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Ledger:
    def __init__(self, path: str):
        self.path = path
        self.entries: list[LedgerEntry] = []
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.path):
            return
        with open(self.path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.entries = [LedgerEntry(**e) for e in raw]

    def save(self) -> None:
        dirname = os.path.dirname(self.path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([asdict(e) for e in self.entries], f, ensure_ascii=False, indent=2)

    # ---- Abfragen (E1/E2/E3/E5/D5) ---------------------------------------

    def find_by_file_hash(self, file_hash: str) -> LedgerEntry | None:
        return next((e for e in self.entries if e.file_hash == file_hash), None)

    def find_by_supplier_and_invoice_number(self, supplier_name: str | None, invoice_number: str | None) -> LedgerEntry | None:
        if not supplier_name or not invoice_number:
            return None
        sn = supplier_name.strip().lower()
        inv = invoice_number.strip().lower()
        return next(
            (e for e in self.entries if (e.supplier_name or "").strip().lower() == sn and (e.invoice_number or "").strip().lower() == inv),
            None,
        )

    def find_content_duplicate(self, line_items_fp: str, gross_amount: float | None, exclude_invoice_number: str | None) -> LedgerEntry | None:
        for e in self.entries:
            if e.line_items_fp != line_items_fp:
                continue
            if exclude_invoice_number and e.invoice_number == exclude_invoice_number:
                continue
            if gross_amount is not None and e.gross_amount is not None and abs(e.gross_amount - gross_amount) > 0.02:
                continue
            return e
        return None

    def cumulative_quantity_for_order(self, order_reference: str | None, exclude_invoice_number: str | None = None) -> float:
        if not order_reference:
            return 0.0
        total = 0.0
        for e in self.entries:
            if e.order_reference != order_reference:
                continue
            if exclude_invoice_number and e.invoice_number == exclude_invoice_number:
                continue
            total += e.total_quantity or 0.0
        return total

    def previous_ibans_for_supplier(self, supplier_name: str | None) -> set[str]:
        if not supplier_name:
            return set()
        sn = supplier_name.strip().lower()
        return {e.supplier_iban for e in self.entries if e.supplier_iban and (e.supplier_name or "").strip().lower() == sn}

    # ---- Schreiben ----------------------------------------------------

    def record(self, entry: LedgerEntry) -> None:
        self.entries.append(entry)
