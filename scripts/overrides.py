"""
Menschliche Übersteuerung einzelner Entscheidungen (Review-Workflow in der UI).

Bewusst getrennt vom automatischen Ergebnis gespeichert: die automatische
Entscheidung (System) und die manuelle Entscheidung (Mensch, nach Ansehen des
Originalbelegs) bleiben beide sichtbar - nie wird die eine durch die andere
stillschweigend ersetzt. Das ist die Grundlage für Nachvollziehbarkeit/Audit.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone


def load(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def set_override(path: str, doc_id: str, decision: str, note: str, original_decision: str) -> dict:
    data = load(path)
    data[doc_id] = {
        "entscheidung": decision,
        "notiz": note,
        "automatisch_war": original_decision,
        "zeitpunkt": datetime.now(timezone.utc).isoformat(),
    }
    save(path, data)
    return data[doc_id]
