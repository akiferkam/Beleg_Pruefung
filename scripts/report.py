"""Erzeugt ergebnis.csv und ergebnis.md aus den verarbeiteten Belegen."""
from __future__ import annotations

import csv
import os

FIELDNAMES = [
    "doc_id", "datei", "entscheidung", "lieferant", "rechnungsnr", "betrag_brutto_eur",
    "bestellnummer", "gruende", "info_notes", "quelle", "automatisch_war", "manuelle_notiz",
]


def write_csv(path: str, rows: list[dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, delimiter=";", restval="")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_markdown(path: str, rows: list[dict], generated_at: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    freigegeben = [r for r in rows if r["entscheidung"] == "freigeben"]
    hinschauen = [r for r in rows if r["entscheidung"] == "hinschauen"]

    lines = []
    lines.append("# Ergebnis Beleg-Prüfung\n")
    lines.append(f"Erzeugt: {generated_at}\n")
    lines.append(f"\n**{len(freigegeben)} freigeben / {len(hinschauen)} hinschauen** von {len(rows)} Belegen.\n")

    lines.append("\n## Übersicht\n")
    lines.append("| Beleg | Entscheidung | Lieferant | Rechnungsnr. | Betrag brutto | Bestellnr. |")
    lines.append("|---|---|---|---|---|---|")
    for r in rows:
        marker = " (manuell)" if r.get("quelle") == "manuell" else ""
        lines.append(f"| {r['doc_id']} | **{r['entscheidung']}{marker}** | {r['lieferant'] or '-'} | {r['rechnungsnr'] or '-'} | {r['betrag_brutto_eur'] or '-'} | {r['bestellnummer'] or '-'} |")

    lines.append("\n## Details\n")
    for r in rows:
        lines.append(f"\n### {r['doc_id']} — {r['entscheidung'].upper()}\n")
        lines.append(f"- Lieferant: {r['lieferant'] or '-'}")
        lines.append(f"- Rechnungsnr.: {r['rechnungsnr'] or '-'}")
        lines.append(f"- Betrag brutto: {r['betrag_brutto_eur'] or '-'}")
        lines.append(f"- Bestellnummer: {r['bestellnummer'] or '-'}")
        if r.get("quelle") == "manuell":
            lines.append(f"- **Manuell übersteuert** (automatisch war: {r.get('automatisch_war', '-')}). Notiz: {r.get('manuelle_notiz') or '-'}")
        if r["entscheidung"] == "hinschauen":
            lines.append("- Gründe:")
            for g in r["gruende"].split(" || "):
                if g:
                    lines.append(f"  - {g}")
        if r.get("info_notes"):
            lines.append("- Zur Information (nicht blockierend):")
            for note in r["info_notes"].split(" || "):
                if note:
                    lines.append(f"  - {note}")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
