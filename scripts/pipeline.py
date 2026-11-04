"""
Gemeinsame Kernpipeline für CLI (run.py) und Web-API (api/app.py).

Trennt bewusst "Analyse" (keine Ledger-Schreibung) von "Übernahme" (Ledger
wird fortgeschrieben): im Gespräch soll man einen Schwellenwert live ändern
und beliebig oft neu auswerten können, ohne bei jedem Klick das Ledger mit
Test-Durchläufen zu verschmutzen oder erneut für die Extraktion zu bezahlen.
Die Extraktion wird deshalb dateiinhaltsbasiert (Hash) gecacht - eine
Config-Änderung löst nur eine neue Auswertung aus, keine neue Vision-Anfrage.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

import checks
import decide as decide_module
import extract
import intake
import ledger as ledger_module
import normalize
import po as po_module
from anthropic import Anthropic


@dataclass
class ProcessedDoc:
    doc_id: str
    path: str
    intake_result: object
    file_hash: str
    extraction: dict | None
    extraction_error: str | None
    findings: list
    decision: object
    extra_ctx: dict


def find_belege(folder: str) -> list[str]:
    paths = []
    for entry in sorted(os.listdir(folder)):
        full = os.path.join(folder, entry)
        if os.path.isfile(full) and os.path.splitext(entry)[1].lower() != ".csv":
            paths.append(full)
    return paths


def _extract_with_cache(client: Anthropic, model: str, max_tokens: int, ir, file_hash: str, cache_dir: str | None):
    cache_path = os.path.join(cache_dir, f"{file_hash}.json") if cache_dir else None
    if cache_path and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f), None

    extraction, err = extract.extract_document_safe(client, model, max_tokens, ir)

    if extraction is not None and cache_path:
        os.makedirs(cache_dir, exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(extraction, f, ensure_ascii=False)
    return extraction, err


def ledger_entry_for(doc: ProcessedDoc) -> ledger_module.LedgerEntry:
    extraction = doc.extraction
    po = doc.extra_ctx.get("po")
    matched = doc.extra_ctx.get("matched_items") or []
    if po is not None:
        total_qty = sum((i.get("quantity") or 0) for i in matched)
    else:
        total_qty = sum((i.get("quantity") or 0) for i in (extraction.get("line_items") or []))
    return ledger_module.LedgerEntry(
        doc_id=doc.doc_id, file_hash=doc.file_hash,
        supplier_name=extraction.get("supplier_name"), invoice_number=extraction.get("invoice_number"),
        invoice_date=extraction.get("invoice_date"), order_reference=extraction.get("order_reference"),
        net_amount=extraction.get("net_amount"), gross_amount=extraction.get("gross_amount"),
        total_quantity=total_qty, line_items_fp=doc.extra_ctx.get("fingerprint", ""),
        supplier_iban=normalize.normalize_iban(extraction.get("supplier_iban")),
        decision=doc.decision.status,
    )


def process_folder(
    *, folder: str, orders_csv: str, ledger_path: str, config: dict,
    client: Anthropic, extraction_cache_dir: str | None = None,
    commit_to_ledger: bool = True, progress=None,
) -> tuple[list[ProcessedDoc], ledger_module.Ledger]:
    """Verarbeitet alle Belege in `folder`. Lädt das Ledger immer frisch vom
    Datenträger (Vorschau-Läufe starten also nie auf einem verschmutzten
    Zwischenstand). Schreibt das Ledger nur zurück, wenn commit_to_ledger=True.
    """
    model = config["model"]["name"]
    max_tokens = config["model"]["max_tokens"]
    orders_db = po_module.load_orders(orders_csv)
    ledg = ledger_module.Ledger(ledger_path)

    records = []
    for path in find_belege(folder):
        ir = intake.load_document(path)
        file_hash = ledger_module.file_sha256(path)
        extraction, err = None, ir.error
        if ir.readable:
            extraction, err = _extract_with_cache(client, model, max_tokens, ir, file_hash, extraction_cache_dir)
        records.append({"path": path, "intake": ir, "file_hash": file_hash, "extraction": extraction, "error": err})
        if progress:
            progress(f"extrahiert: {ir.doc_id}" + (f" -- FEHLER: {err}" if err else ""))

    def sort_key(rec: dict):
        ex = rec["extraction"]
        date_str = ex.get("invoice_date") if ex else None
        return (date_str is None, date_str or "", rec["intake"].doc_id)

    records.sort(key=sort_key)

    processed: list[ProcessedDoc] = []
    for rec in records:
        ir, extraction, err = rec["intake"], rec["extraction"], rec["error"]

        if extraction is not None:
            grounding_report = normalize.check_grounding(extraction, ir.combined_text)
        else:
            grounding_report = normalize.GroundingReport(skipped=True, skip_reason="Keine Extraktion verfügbar.")

        findings, extra_ctx = checks.run_all_checks(
            intake_result=ir, extraction=extraction, extraction_error=err,
            grounding_report=grounding_report, orders_db=orders_db, ledger=ledg,
            config=config, file_hash=rec["file_hash"],
        )
        decision = decide_module.decide(findings)

        doc = ProcessedDoc(
            doc_id=ir.doc_id, path=rec["path"], intake_result=ir, file_hash=rec["file_hash"],
            extraction=extraction, extraction_error=err, findings=findings, decision=decision, extra_ctx=extra_ctx,
        )
        processed.append(doc)

        if extraction is not None:
            ledg.record(ledger_entry_for(doc))  # im Speicher - beeinflusst Folgebelege in diesem Lauf

        if progress:
            n_reasons = len(decision.blocking_reasons)
            progress(f"entschieden: {ir.doc_id}: {decision.status}" + (f" ({n_reasons} Grund/Gründe)" if n_reasons else ""))

    if commit_to_ledger:
        ledg.save()

    return processed, ledg


def rows_for_report(processed: list[ProcessedDoc]) -> list[dict]:
    rows = []
    for doc in processed:
        extraction = doc.extraction
        rows.append({
            "doc_id": doc.doc_id,
            "datei": os.path.basename(doc.path),
            "entscheidung": doc.decision.status,
            "lieferant": extraction.get("supplier_name") if extraction else None,
            "rechnungsnr": extraction.get("invoice_number") if extraction else None,
            "betrag_brutto_eur": extraction.get("gross_amount") if extraction else None,
            "bestellnummer": extraction.get("order_reference") if extraction else None,
            "gruende": " || ".join(f"[{f.check_id}] {f.message}" for f in doc.decision.blocking_reasons),
            "info_notes": " || ".join(f"[{f.check_id}] {f.message}" for f in doc.decision.info_notes),
        })
    rows.sort(key=lambda r: r["doc_id"])
    return rows
