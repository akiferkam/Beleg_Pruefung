"""Lädt bestellungen.csv zu Lookup-Objekten."""
from __future__ import annotations

import csv
from dataclasses import dataclass


@dataclass
class PurchaseOrder:
    bestellnummer: str
    lieferant: str
    artikel: str
    menge: float
    einzelpreis_netto: float

    @property
    def is_rahmenvertrag(self) -> bool:
        """Einzelpreis 0 = Sammel-/Rahmenbestellung ohne festen Stückpreis (D7)."""
        return self.einzelpreis_netto == 0


def load_orders(path: str) -> dict[str, PurchaseOrder]:
    orders: dict[str, PurchaseOrder] = {}
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            po = PurchaseOrder(
                bestellnummer=row["Bestellnummer"].strip(),
                lieferant=row["Lieferant"].strip(),
                artikel=row["Artikel"].strip(),
                menge=float(row["Menge"]),
                einzelpreis_netto=float(row["Einzelpreis_netto_EUR"]),
            )
            orders[po.bestellnummer] = po
    return orders
