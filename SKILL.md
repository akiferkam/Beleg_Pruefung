---
name: beleg-pruefung
description: Prüft Lieferantenbelege (Rechnungen als PDF, JPG, PNG, ...) aus einem Ordner gegen bestellungen.csv und entscheidet pro Beleg "freigeben" oder "hinschauen", mit nachvollziehbarer Begründung. Benutzen, wenn jemand einen Ordner mit Belegen/Rechnungen prüfen, gegen Bestellungen abgleichen oder zur Zahlung freigeben lassen möchte.
---

# Beleg-Prüfung für Quellberg

Prüft beliebig viele Belege (beliebiges Format: PDF, JPG, PNG, TIFF, WEBP, ...)
aus einem Ordner automatisch gegen `bestellungen.csv` und entscheidet pro Beleg:
**freigeben** oder **hinschauen**. Die Entscheidung wird ausschließlich
deterministisch in Python getroffen (`scripts/checks/`); ein LLM (Claude Vision)
wird nur zur Extraktion der Belegdaten in ein festes JSON-Schema genutzt, nie
zur Entscheidung selbst - siehe README.md für die Begründung.

## Voraussetzungen

- Python 3.11+, Pakete aus `requirements.txt` (`pip install -r requirements.txt`).
- Umgebungsvariable `ANTHROPIC_API_KEY` (oder eine `.env`-Datei im Projektroot
  mit `ANTHROPIC_API_KEY=...`).

## Benutzung

```
python scripts/run.py <ordner-mit-belegen> [--orders bestellungen.csv] [--out results]
```

- `<ordner-mit-belegen>`: Ordner mit beliebig vielen Belegdateien. Nicht-Beleg-Dateien
  (außer `.csv`) werden ebenfalls verarbeitet und fallen bei Nichtlesbarkeit automatisch
  auf `hinschauen` (Check A1) statt stillschweigend übersprungen zu werden.
- `--orders`: Pfad zu `bestellungen.csv`. Default: Datei gleichen Namens im Belege-Ordner,
  sonst der in `config.yaml` hinterlegte Pfad.
- `--out`: Ausgabeverzeichnis für Ergebnisse. Default: `results/` (aus `config.yaml`).

Ergebnis:
- `results/ergebnis.csv` - eine Zeile pro Beleg (Entscheidung, Lieferant, Beträge, Gründe).
- `results/ergebnis.md` - dieselben Ergebnisse menschenlesbar, mit vollständiger
  Begründung pro Beleg (auch bei freigeben: alle geprüften Punkte sind aufgeführt,
  z.B. wie nah eine Toleranzgrenze gerissen wurde).
- `results/extracted/<beleg>.json` - die rohe Extraktion pro Beleg (Transparenz/Debugging).
- `ledger/ledger.json` - laufübergreifendes Gedächtnis (Duplikate, kumulierte Mengen
  pro Bestellung, bekannte IBANs pro Lieferant). Wächst mit jedem Lauf weiter; für
  einen komplett frischen Testlauf vorher löschen.

Alternativ: `python api/app.py` (API) + `cd web && npm run dev` (React-UI,
`http://localhost:8080`) für Hochladen/Analysieren mit Dashboard, Warteschlange,
Belegdetails und live editierbaren Policy-Werten - siehe README.md, Abschnitt
"Drei Wege, den Skill zu benutzen".

## Live-Änderungen (für das Gespräch)

Alle Schwellenwerte und Policies stehen in `config.yaml`, nichts ist im Code
hartkodiert. Typische Live-Änderungen, ohne Code anzufassen:

- `policy.extra_items_tolerance_pct` (Standard 10%) - Toleranz für nicht bestellte
  Zusatzpositionen. Senken auf z.B. 9% lässt b01 (9,9% Zusatzposition) sofort auf
  hinschauen kippen.
- `policy.mandatory_review_amount_eur` (Standard 50.000 €) - Vier-Augen-Grenze.
  Senken auf z.B. 20.000 € lässt b02 (25.235,62 €) sofort auf hinschauen kippen.
- `policy.no_po_match_means_hinschauen` - ob Belege ohne Bestellbezug automatisch
  hinschauen auslösen (siehe README, Policy-Entscheidung).

Eine neue Prüfung hinzuzufügen bedeutet: eine Funktion in `scripts/checks/*.py`
schreiben, die ein `Finding` zurückgibt, und sie in `scripts/checks/__init__.py`
in `run_all_checks()` einhängen - kein Eingriff in Extraktion oder Entscheidungslogik nötig.

## Aufbau

Siehe README.md für die vollständige Architektur- und Qualitätsbeschreibung.
Kurzfassung: `intake.py` (Format → Bilder+Text) → `extract.py` (Claude Vision →
festes JSON-Schema) → `normalize.py` (Grounding gegen Halluzination) →
`checks/` (reine Python-Regeln, Katalog A-F) → `decide.py` (freigeben/hinschauen)
→ `report.py` (Ausgabe). `ledger.py` hält das laufübergreifende Gedächtnis für
Duplikats- und Mengenprüfungen. `pipeline.py` bündelt diese Schritte zu einem
wiederverwendbaren Kern, den `scripts/run.py` (CLI) und `api/app.py` (JSON-API
für `web/`, das React-Frontend) beide aufrufen - gleiche Regeln, egal welchen
der drei Wege man nutzt.
