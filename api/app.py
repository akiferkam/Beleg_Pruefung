#!/usr/bin/env python3
"""
Beleg-Prüfung für Quellberg — JSON-API für das Web-Frontend (web/, React).

Dünner Aufsatz auf dieselbe Pipeline wie die CLI (scripts/pipeline.py). Reine
API (kein HTML-Rendering) - die Oberfläche lebt komplett in web/, das diese
Endpunkte per fetch() aufruft (siehe web/src/lib/api/rest.ts).

Zwei Modi:
  - "Analysieren": Vorschau, schreibt NICHTS ins Ledger (beliebig oft
    wiederholbar, z.B. nach einer Config-Änderung - ohne Zwischenstände
    zu verschmutzen oder erneut für die Extraktion zu bezahlen, dank
    Extraktions-Cache in pipeline.py).
  - "In Ledger übernehmen": wie ein echter CLI-Lauf - schreibt das Ledger
    fort und aktualisiert results/ergebnis.csv / .md.

Start: python api/app.py   (API dann auf http://127.0.0.1:5050)
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "scripts"))

import yaml  # noqa: E402
from anthropic import Anthropic  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from flask import Flask, Response, abort, jsonify, request, send_file  # noqa: E402
from flask_cors import CORS  # noqa: E402

import overrides as overrides_mod  # noqa: E402
import pipeline  # noqa: E402
import report  # noqa: E402
import thumbnails  # noqa: E402

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.yaml")
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
CACHE_DIR = os.path.join(PROJECT_ROOT, ".cache", "extracted")
THUMB_CACHE_DIR = os.path.join(PROJECT_ROOT, ".cache", "thumbs")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
OVERRIDES_PATH = os.path.join(RESULTS_DIR, "overrides.json")
VIEWABLE_SUFFIXES = {".pdf", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}

app = Flask(__name__)
# Nur für /api/*: erlaubt dem lokalen Vite-Dev-Server (anderer Port), die JSON-API
# per fetch() aufzurufen. /doc und /thumb brauchen das nicht (<img>/<a> sind nicht
# CORS-pflichtig) und bleiben bewusst ungeöffnet.
CORS(app, resources={r"/api/*": {"origins": r"http://(localhost|127\.0\.0\.1):\d+"}})
_client: Anthropic | None = None


def client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic()
    return _client


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def apply_overrides(config: dict, overrides: dict) -> dict:
    """Wendet Live-Overrides aus der UI auf eine Kopie der Policy an -
    config.yaml selbst bleibt unangetastet, solange man nicht explizit speichert."""
    policy = dict(config["policy"])
    for key in ("extra_items_tolerance_pct", "mandatory_review_amount_eur", "line_arithmetic_tolerance_per_unit_eur"):
        if key in overrides and overrides[key] not in (None, ""):
            policy[key] = float(overrides[key])
    if "no_po_match_means_hinschauen" in overrides:
        policy["no_po_match_means_hinschauen"] = bool(overrides["no_po_match_means_hinschauen"])
    merged = dict(config)
    merged["policy"] = policy
    return merged


def resolve_orders_csv(config: dict, folder: str) -> str:
    candidate = os.path.join(folder, "bestellungen.csv")
    if os.path.exists(candidate):
        return candidate
    return os.path.join(PROJECT_ROOT, config["paths"]["orders_csv"])


def serialize(processed: list[pipeline.ProcessedDoc], upload_folder: str | None = None) -> list[dict]:
    overrides = overrides_mod.load(OVERRIDES_PATH)
    out = []
    for doc in processed:
        ex = doc.extraction or {}
        override = overrides.get(doc.doc_id)
        abs_path = os.path.abspath(doc.path)
        out.append({
            "doc_id": doc.doc_id,
            "datei": os.path.basename(doc.path),
            "pfad": abs_path,
            "neu_hochgeladen": bool(upload_folder) and abs_path.startswith(os.path.abspath(upload_folder)),
            "entscheidung": doc.decision.status,
            "endstatus": override["entscheidung"] if override else doc.decision.status,
            "manuell": override,
            "lieferant": ex.get("supplier_name"),
            "rechnungsnr": ex.get("invoice_number"),
            "betrag_brutto_eur": ex.get("gross_amount"),
            "bestellnummer": ex.get("order_reference"),
            "gruende": [{"id": f.check_id, "nachricht": f.message} for f in doc.decision.blocking_reasons],
            "info_notes": [{"id": f.check_id, "nachricht": f.message} for f in doc.decision.info_notes],
            "fehler": doc.extraction_error,
            # Zusätzliche Detailfelder (für die Beleg-Detailansicht) - nicht
            # entscheidungsrelevant, rein informativ, direkt aus der Extraktion.
            "belegtyp": ex.get("document_type"),
            "lieferant_adresse": ex.get("supplier_address"),
            "lieferant_steuernr": ex.get("supplier_tax_id"),
            "iban": ex.get("supplier_iban"),
            "rechnungsdatum": ex.get("invoice_date"),
            "betrag_netto_eur": ex.get("net_amount"),
            "ust_satz_pct": ex.get("vat_rate_pct"),
            "ust_betrag_eur": ex.get("vat_amount"),
            "skonto": ex.get("skonto_terms"),
            "manipulationsversuch": ex.get("manipulation_attempt"),
            "positionen": [
                {
                    "beschreibung": item.get("description"),
                    "menge": item.get("quantity"),
                    "einzelpreis": item.get("unit_price"),
                    "gesamt": item.get("line_total"),
                }
                for item in (ex.get("line_items") or [])
            ],
        })
    out.sort(key=lambda r: r["doc_id"])
    return out


@app.route("/")
def index():
    """Kein UI mehr hier - die Oberfläche läuft unter web/ (React, siehe README)."""
    return jsonify({"status": "ok", "service": "beleg-pruefung-api", "ui": "siehe web/ (npm run dev)"})


@app.route("/api/upload", methods=["POST"])
def api_upload():
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "Keine Dateien hochgeladen."}), 400
    batch_dir = os.path.join(UPLOAD_DIR, datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6])
    os.makedirs(batch_dir, exist_ok=True)
    saved = []
    for f in files:
        if not f.filename:
            continue
        dest = os.path.join(batch_dir, os.path.basename(f.filename))
        f.save(dest)
        saved.append(os.path.basename(f.filename))
    return jsonify({"folder": batch_dir, "dateien": saved})


def _run(commit: bool):
    body = request.get_json(force=True)
    folder = body.get("folder") or os.path.join(PROJECT_ROOT, "belege")
    overrides = body.get("policy") or {}

    if not os.path.isdir(folder):
        return jsonify({"error": f"Ordner nicht gefunden: {folder}"}), 400

    config = apply_overrides(load_config(), overrides)
    orders_csv = resolve_orders_csv(config, folder)
    ledger_path = os.path.join(PROJECT_ROOT, config["paths"]["ledger_file"])

    processed, _ledg = pipeline.process_folder(
        folder=folder, orders_csv=orders_csv, ledger_path=ledger_path, config=config,
        client=client(), extraction_cache_dir=CACHE_DIR, commit_to_ledger=commit,
    )

    if commit:
        rows = pipeline.rows_for_report(processed)
        overrides = overrides_mod.load(OVERRIDES_PATH)
        for row in rows:
            override = overrides.get(row["doc_id"])
            if override:
                row["automatisch_war"] = row["entscheidung"]
                row["entscheidung"] = override["entscheidung"]
                row["quelle"] = "manuell"
                row["manuelle_notiz"] = override["notiz"]
            else:
                row["quelle"] = "automatisch"
        report.write_csv(os.path.join(RESULTS_DIR, "ergebnis.csv"), rows)
        report.write_markdown(os.path.join(RESULTS_DIR, "ergebnis.md"), rows, datetime.now(timezone.utc).isoformat())
        extracted_dir = os.path.join(RESULTS_DIR, "extracted")
        os.makedirs(extracted_dir, exist_ok=True)
        for doc in processed:
            if doc.extraction is not None:
                with open(os.path.join(extracted_dir, f"{doc.doc_id}.json"), "w", encoding="utf-8") as f:
                    json.dump(doc.extraction, f, ensure_ascii=False, indent=2)

    upload_folder = folder if os.path.abspath(folder).startswith(os.path.abspath(UPLOAD_DIR)) else None
    docs = serialize(processed, upload_folder)
    n_free = sum(1 for d in docs if d["endstatus"] == "freigeben")
    return jsonify({
        "docs": docs,
        "summary": {"freigeben": n_free, "hinschauen": len(docs) - n_free, "gesamt": len(docs)},
        "committed": commit,
        "policy_used": config["policy"],
    })


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    return _run(commit=False)


@app.route("/api/commit", methods=["POST"])
def api_commit():
    return _run(commit=True)


@app.route("/doc")
def view_doc():
    """Liefert den Original-Beleg (PDF/Bild) aus - für 'anschauen, bevor man entscheidet'.
    Lokal gebunden (127.0.0.1); trotzdem nur bekannte Beleg-Endungen, keine beliebigen Dateien."""
    path = request.args.get("path", "")
    if not path or not os.path.isfile(path):
        abort(404)
    if os.path.splitext(path)[1].lower() not in VIEWABLE_SUFFIXES:
        abort(403)
    return send_file(os.path.abspath(path))


@app.route("/thumb")
def view_thumb():
    """Kleines Vorschaubild (erste Seite/Bild) - für Kartenansicht und Upload-Vorschau."""
    path = request.args.get("path", "")
    if not path or not os.path.isfile(path):
        abort(404)
    if os.path.splitext(path)[1].lower() not in VIEWABLE_SUFFIXES:
        abort(403)
    try:
        data = thumbnails.get_thumbnail(os.path.abspath(path), THUMB_CACHE_DIR)
    except Exception:
        abort(500)
    return Response(data, mimetype="image/png")


@app.route("/api/override", methods=["POST"])
def api_override():
    """Manuelle Freigabe/Ablehnung nach Ansehen des Originalbelegs.
    Automatische und manuelle Entscheidung bleiben beide sichtbar (siehe overrides.py)."""
    body = request.get_json(force=True)
    doc_id = body.get("doc_id")
    decision = body.get("decision")
    original = body.get("original_decision", "")
    note = (body.get("note") or "").strip()
    if not doc_id or decision not in ("freigeben", "hinschauen"):
        return jsonify({"error": "doc_id und decision ('freigeben'|'hinschauen') erforderlich."}), 400
    record = overrides_mod.set_override(OVERRIDES_PATH, doc_id, decision, note, original)
    return jsonify({"doc_id": doc_id, "manuell": record})


if __name__ == "__main__":
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    app.run(host="127.0.0.1", port=5050, debug=False, threaded=True)
