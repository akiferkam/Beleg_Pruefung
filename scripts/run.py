#!/usr/bin/env python3
"""
Beleg-Prüfung für Quellberg — Haupteinstiegspunkt (CLI).

Aufruf:
    python scripts/run.py <belege-ordner> [--orders bestellungen.csv] [--out results]

Verarbeitet jede Datei im Ordner (beliebiges Format: PDF, JPG, PNG, ...),
entscheidet pro Beleg freigeben/hinschauen und schreibt results/ergebnis.csv
und results/ergebnis.md. Die Entscheidung wird ausschließlich in Python
(checks/) getroffen - das LLM (extract.py) liefert nur strukturierte Daten.

Die eigentliche Pipeline steckt in pipeline.py und wird von diesem CLI-Skript
und von ui/app.py (Web-Oberfläche) gemeinsam genutzt.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml  # noqa: E402
from anthropic import Anthropic  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

import pipeline  # noqa: E402
import report  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_orders_csv(args_orders: str | None, folder: str, config: dict) -> str:
    if args_orders:
        return args_orders
    candidate = os.path.join(folder, "bestellungen.csv")
    if os.path.exists(candidate):
        return candidate
    return os.path.join(PROJECT_ROOT, config["paths"]["orders_csv"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Beleg-Prüfung für Quellberg")
    parser.add_argument("folder", help="Ordner mit Belegen (PDF/JPG/PNG/...)")
    parser.add_argument("--orders", default=None, help="Pfad zu bestellungen.csv (Default: im Belege-Ordner oder config.yaml)")
    parser.add_argument("--config", default=os.path.join(PROJECT_ROOT, "config.yaml"))
    parser.add_argument("--out", default=None, help="Ausgabeverzeichnis (Default: config.yaml results_dir)")
    parser.add_argument("--ledger", default=None, help="Pfad zur Ledger-Datei (Default: config.yaml ledger_file) - z.B. für isolierte Demo-/Testläufe")
    parser.add_argument("--no-cache", action="store_true", help="Extraktions-Cache ignorieren, jeden Beleg neu per Vision-API lesen")
    args = parser.parse_args()

    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
    config = load_config(args.config)

    orders_csv = resolve_orders_csv(args.orders, args.folder, config)
    out_dir = args.out or os.path.join(PROJECT_ROOT, config["paths"]["results_dir"])
    extracted_dir = os.path.join(out_dir, "extracted")
    os.makedirs(extracted_dir, exist_ok=True)
    ledger_path = args.ledger or os.path.join(PROJECT_ROOT, config["paths"]["ledger_file"])
    cache_dir = None if args.no_cache else os.path.join(PROJECT_ROOT, ".cache", "extracted")

    client = Anthropic()

    processed, _ledg = pipeline.process_folder(
        folder=args.folder, orders_csv=orders_csv, ledger_path=ledger_path, config=config,
        client=client, extraction_cache_dir=cache_dir, commit_to_ledger=True, progress=print,
    )

    import json
    for doc in processed:
        if doc.extraction is not None:
            with open(os.path.join(extracted_dir, f"{doc.doc_id}.json"), "w", encoding="utf-8") as f:
                json.dump(doc.extraction, f, ensure_ascii=False, indent=2)

    rows = pipeline.rows_for_report(processed)
    report.write_csv(os.path.join(out_dir, "ergebnis.csv"), rows)
    report.write_markdown(os.path.join(out_dir, "ergebnis.md"), rows, datetime.now(timezone.utc).isoformat())

    n_free = sum(1 for r in rows if r["entscheidung"] == "freigeben")
    print(f"\nFertig: {n_free} freigeben / {len(rows) - n_free} hinschauen von {len(rows)} Belegen. Ergebnisse in {out_dir}")


if __name__ == "__main__":
    main()
