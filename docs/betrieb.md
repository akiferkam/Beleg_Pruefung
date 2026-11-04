# Installation und Betrieb

## Python-Umgebung unter Windows

Die folgenden Befehle gehören in PowerShell im Projektordner. Sie beschreiben die Einrichtung der Anwendung, nicht des Dokumentationswerkzeugs.

```powershell
cd "C:\Users\akife\Desktop\beleg_pruefer_akif"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` enthält Anthropic, PyMuPDF, Pillow, PyYAML, python-dotenv, RapidFuzz, Flask und Flask-CORS. Eine konkrete Mindestversion von Python wird dort nicht festgelegt; der Code verwendet unter anderem moderne Union-Typen.

Für neue Extraktionen wird `ANTHROPIC_API_KEY` benötigt. Die Anwendung lädt die `.env` im Projektstamm. Eine neue Datei lässt sich beispielsweise mit `notepad .env` anlegen; eine vorhandene Datei vorher prüfen und erhalten.

```dotenv
ANTHROPIC_API_KEY=HIER_DEN_EIGENEN_SCHLUESSEL_EINTRAGEN
```

Der Modellname stammt aus `config.yaml` unter `model.name`; im untersuchten Stand ist dort `claude-sonnet-5` eingetragen. Ob dieser Bezeichner für das verwendete Konto verfügbar ist, wurde nicht durch einen API-Aufruf geprüft. Modellzugang und API-Schlüssel sind Voraussetzung für eine erfolgreiche neue Extraktion.

## Web-Oberfläche im Live-Modus

In einem ersten Terminal im Projektstamm:

```powershell
.\.venv\Scripts\python.exe api\app.py
```

Die API bindet an `http://127.0.0.1:5050`. In einem zweiten Terminal:

```powershell
cd "C:\Users\akife\Desktop\beleg_pruefer_akif\web"
npm install --legacy-peer-deps
$env:VITE_BELEG_API_URL = "http://127.0.0.1:5050"
npm run dev
```

Die Projektanleitung nennt `http://localhost:8080` für die Oberfläche; maßgeblich ist die tatsächlich von Vite ausgegebene Adresse. Die Umgebungsvariable gilt für den gestarteten Prozess und wird beim Build beziehungsweise Start von Vite eingelesen. Alternativ kann sie in `web/.env` hinterlegt werden.

Die Oberfläche startet beim Laden eine Analyse. Neue, noch nicht gecachte Dokumente können dabei bereits Vision-Aufrufe auslösen. „Analysieren“ schreibt keine Ledger-Historie, kann aber Extraktionscaches erzeugen.

## Demo ohne Backend

Ohne gesetztes `VITE_BELEG_API_URL` wählt `web/src/lib/api/index.ts` den Mock-Adapter. Für eine aktuelle PowerShell-Sitzung:

```powershell
Remove-Item Env:VITE_BELEG_API_URL -ErrorAction SilentlyContinue
npm run dev
```

Auch in `web/.env` und anderen Vite-Umgebungsdateien darf dann kein Wert gesetzt sein. Der Demo-Modus verwendet gespeicherte Beispieldaten und bildet keinen echten neuen Extraktionslauf ab.

## CLI

```powershell
cd "C:\Users\akife\Desktop\beleg_pruefer_akif"
.\.venv\Scripts\python.exe scripts\run.py belege\
```

Dieser Aufruf schreibt direkt ins konfigurierte Ledger. Es existiert in `run.py` kein Vorschau-Schalter.

| Option | Bedeutung |
|---|---|
| `folder` | Zu verarbeitender Ordner, ohne rekursive Unterordnersuche |
| `--orders` | Expliziter Pfad zur Bestell-CSV |
| `--config` | Alternative YAML-Konfiguration |
| `--out` | Verzeichnis für CSV, Markdown und Extraktionskopien |
| `--ledger` | Alternative Historie, etwa für isolierte Testläufe |
| `--no-cache` | Vorhandenen Extraktionscache umgehen und Ergebnisse dort nicht speichern |

Beispiel für einen vom produktiven Ledger getrennten Lauf:

```powershell
.\.venv\Scripts\python.exe scripts\run.py belege\ --ledger "demo-output\ledger.json" --out "demo-output\results"
```

Ein bereits vorhandenes Demo-Ledger wird auch dabei wieder geladen. Die Bestell-CSV wird in dieser Reihenfolge gesucht: `--orders`, `bestellungen.csv` im Eingabeordner, konfigurierter Standardpfad relativ zum Projektstamm.

## Typische Fehler

| Symptom | Zu prüfende Ursache |
|---|---|
| Oberfläche zeigt weiter Beispieldaten | `VITE_BELEG_API_URL` fehlt; Vite nach Änderung neu starten |
| Netzwerkfehler im Browser | API läuft nicht oder Adresse/Port stimmt nicht |
| A2: Extraktion fehlgeschlagen | API-Schlüssel, Modellzugang oder Netzwerkfehler |
| A1: Datei nicht lesbar | Dateiformat, beschädigte Datei oder PDF-Passwort |
| Viele Duplikatbefunde nach erneutem Lauf | Dokumente stehen bereits im Ledger |
| Geändertes Modell liefert alte Extraktion | Cache ist nur nach Dateiinhalt adressiert; gegebenenfalls `--no-cache` verwenden |
| Ergebnis ändert sich nach Neuladen | Browser-Policy, Ledger-Historie oder initial ausgewählter Ordner |

## Quellen

`requirements.txt`, `config.yaml`, `scripts/run.py::main`, `scripts/run.py::resolve_orders_csv`, `api/app.py`, `web/README.md`, `web/package.json`, `web/src/lib/api/index.ts`.

[Zur Übersicht](overview.md)
