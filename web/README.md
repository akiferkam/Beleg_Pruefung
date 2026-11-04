# Beleg-Prüfung — Web-Oberfläche

React/TanStack-Frontend für die [Beleg-Prüfung](../README.md). Ursprünglich als
Design-Entwurf mit [Lovable](https://lovable.dev) erstellt, dann an die
tatsächliche Python-API (`../api/app.py`) angebunden - kein Mock mehr nötig.

## Starten

```sh
cp .env.example .env    # VITE_BELEG_API_URL=http://127.0.0.1:5050 reicht
npm install --legacy-peer-deps
npm run dev              # http://localhost:8080
```

Parallel dazu muss die API laufen (im Projekt-Root):

```sh
pip install -r ../requirements.txt
python ../api/app.py     # http://127.0.0.1:5050
```

Ohne `VITE_BELEG_API_URL` läuft die App im Demo-Modus mit
`src/lib/mock/sample-results.json` (Ergebnis eines echten Laufs über die 16
Testbelege, aber ohne Live-Verbindung - nützlich zum Durchklicken ohne API-Key).

## Seiten

- `/` — Dashboard (KPIs, Befunde nach Prüfbereich, letzte Aktivitäten)
- `/pruefen` — Warteschlange, eine Karte pro offenem Beleg
- `/belege/$docId` — volle Belegdaten, Original-Vorschau, Entscheidung
- `/freigegeben` — alle entschiedenen Belege (automatisch/manuell)
- `/hochladen` — neue Belege hochladen
- `/pruefregeln` — Policy-Werte live ändern

Siehe [../README.md](../README.md) für die Gesamtarchitektur.
