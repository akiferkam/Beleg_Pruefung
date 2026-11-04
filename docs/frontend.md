# Web-Oberfläche und Zustand

Die Oberfläche verwendet React 19, TanStack Router/Start, Vite, Tailwind und Radix-Komponenten. Anwendungsbezogene Komponenten liegen unter `web/src/components/beleg/`, allgemeine UI-Bausteine unter `web/src/components/ui/`.

## Seiten

| Route | Aufgabe |
|---|---|
| `/` | Dashboard mit Kennzahlen und Aktivitäten |
| `/pruefen` | Warteschlange offener Dokumente |
| `/belege/$docId` | Einzelbeleg mit Befunden, Positionen und Originalvorschau |
| `/freigegeben` | Ansicht entschiedener beziehungsweise freigegebener Dokumente |
| `/hochladen` | Datei-Upload und anschließende Analyse |
| `/pruefregeln` | Änderung der vier vom Client übergebenen Policy-Werte |

Die Routendateien befinden sich unter `web/src/routes/`. `routeTree.gen.ts` ist der generierte Routenbaum. Der Router und die Root-Route stellen das gemeinsame Layout und den Anwendungsprovider bereit.

## API-Abstraktion

`web/src/lib/api/types.ts` definiert `BelegApi`, `BelegResult`, `PolicyOverrides` und weitere gemeinsame Typen. `api/index.ts` wählt abhängig von `VITE_BELEG_API_URL` den REST- oder Mock-Adapter.

Der REST-Adapter übersetzt deutsche/snake_case-Serverfelder in die Frontend-Struktur, etwa `doc_id` nach `docId`, `entscheidung` nach `autoDecision` und `gruende[].nachricht` nach `blockingReasons[].message`. Original- und Vorschau-URLs entstehen aus dem von der API gelieferten Dateipfad.

Der Adapter setzt `currency` fest auf `EUR`, statt einen Serverwert zu übernehmen. Die UI-Währungsanzeige ist damit kein zusätzlicher Nachweis der tatsächlichen Belegwährung.

## Zentraler Store

`BelegProvider` in `web/src/lib/beleg-store.tsx` verwaltet den letzten Lauf, Dokumente, Ladezustand, Policy, aktuellen Eingabeordner, Änderungsstatus, letzten Commitzeitpunkt und Aktivitäten.

| Aktion | Ablauf |
|---|---|
| `analyze` | API aufrufen, Ergebnis ersetzen, als unübernommene Vorschau markieren |
| `commit` | Pipeline-Commit anfordern, Ergebnis ersetzen, Zeit merken und Aktivität erzeugen |
| `decide` | Override serverseitig speichern und manuelle Entscheidung im lokalen Ergebnis ergänzen |
| `setPolicy` | Werte im Browser speichern und sofort erneut analysieren |
| `upload` | Dateien hochladen, Batch-Ordner merken und genau diesen Ordner analysieren |

API-Fehler werden als Toast-Nachricht angezeigt; `finally` setzt den Ladezustand zurück. `RunBar` zeigt Vorschau/Übernahmezustand und öffnet vor dem Commit einen Bestätigungsdialog.

## Persistenz im Browser

| Local-Storage-Schlüssel | Bedeutung |
|---|---|
| `beleg.policy.v1` | Vier UI-Policy-Werte |
| `beleg.folder.v1` | Letzter Eingabeordner |
| `beleg.activity.v1` | Bis zu 60 lokale Aktivitäten |
| `beleg.lastCommit.v1` | Letzter im Browser gemerkter Commitzeitpunkt |

Diese Werte sind browserbezogen. Sie ersetzen weder Backend-Konfiguration noch ein zentrales Auditprotokoll. Die vollständige Dokumentliste wird nach dem Laden neu angefragt.

## Beobachtete Besonderheiten

- `defaultPolicy()` des REST-Adapters liefert die Mock-Standardwerte; es liest nicht die aktuelle `config.yaml` vom Server. Der Store initialisiert ebenfalls mit `DEFAULT_POLICY` beziehungsweise Local Storage und überträgt diese vier Werte an die API.
- Beim ersten Effekt wird zwar ein gespeicherter Ordner in den State geladen, `analyze(p)` verwendet aber noch den im ursprünglichen Callback erfassten Ordner. Der erste Lauf nach Neuladen kann deshalb den Backend-Standardordner analysieren. Spätere Aufrufe nutzen den aktualisierten State.
- Die manuelle Entscheidung wird bereits beim Klick serverseitig gespeichert. „Noch nicht im Ledger“ bedeutet daher nicht, dass keinerlei Datei verändert wurde.
- Der finale UI-Status wird mit `finalDecision` aus manueller oder automatischer Entscheidung berechnet. Die automatische Begründung bleibt dabei verfügbar.

## Build und Entwicklung

```powershell
npm run build
npm run preview
npm run lint
```

Die Befehle sind in `web/package.json` definiert. `npm run format` formatiert Dateien schreibend. Das Vite-Konfigurationspaket bringt bereits React-, TanStack-, Tailwind- und weitere Plugins mit; `vite.config.ts` warnt vor doppelter Registrierung.

## Quellen

`web/package.json`, `web/vite.config.ts`, `web/src/routes/`, `web/src/lib/beleg-store.tsx`, `web/src/lib/api/`, `web/src/components/beleg/run-bar.tsx`.

[Zur Übersicht](overview.md) · [Evaluation und Wartung](evaluation.md)
