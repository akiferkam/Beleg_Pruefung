# Evaluation, Wartung und Grenzen

## Vorhandene Auswertung

`eval/eval.py` vergleicht eine Ergebnis-CSV mit einer Ground-Truth-CSV über `doc_id`. Beide Dateien werden mit Semikolon als Trennzeichen und UTF-8-BOM-Unterstützung gelesen.

```powershell
python eval\eval.py --ergebnis results\ergebnis.csv --ground-truth eval\ground_truth.csv
```

Die Ergebnisdatei benötigt `entscheidung`, die Ground Truth `erwartete_entscheidung`. Als positives Ereignis gilt `hinschauen`:

| Kennzahl | Bedeutung |
|---|---|
| TP | Erwartet hinschauen, erhalten hinschauen |
| TN | Erwartet freigeben, erhalten freigeben |
| FP | Unnötige manuelle Prüfung |
| FN | Erwartet hinschauen, trotzdem freigegeben |

Der Bericht betont FN als gefährliche Fehlfreigabe. Fehlende IDs erzeugen eine Warnung und werden nicht in den Nenner der Accuracy aufgenommen. Doppelte IDs in einer CSV überschreiben sich im eingelesenen Dictionary. Der Evaluator setzt bei Fehlfreigaben keinen eigenen fehlschlagenden Prozess-Exitcode; seine Ausgabe muss daher für CI gezielt ausgewertet oder der Evaluator erweitert werden.

Die Projekt-README nennt für die 16 mitgelieferten Testbelege 3 Freigaben und 13 Fälle zum Hinschauen. Dies ist ein dokumentiertes Beispielergebnis und keine bei der Erstellung dieser Wiki neu durchgeführte Vision-Auswertung.

## Weitere Testwerkzeuge

`eval/generate_synthetic_set.py` erzeugt synthetisches Testmaterial; `eval/generate_injection_demo.py` dient einem Manipulationsbeispiel. Die Generatoren gehören zum Test- und Demonstrationsbereich und sind kein Bestandteil des normalen Web-Requestpfads.

## Eine neue Regel ergänzen

1. Regel im passenden Modul von `scripts/checks/` als Funktion mit `Finding`-Rückgabe implementieren.
2. Eindeutige Prüf-ID, aussagekräftige Nachricht und bewusste Stufe `BLOCK` oder `INFO` wählen.
3. Aufruf in `checks.run_all_checks` an einer zur Datenverfügbarkeit passenden Stelle einfügen.
4. Falls nötig den Schwellenwert in `config.yaml` ergänzen und explizit übergeben.
5. Grenzfälle und fehlende Eingabewerte anhand isolierter Datensätze überprüfen.
6. Für eine neue UI-Policy zusätzlich API-Freigabeliste, TypeScript-Typen und Oberfläche anpassen.

## Extraktion erweitern

Neue Felder gehören zunächst in `EXTRACTION_SCHEMA` und gegebenenfalls in den Prompt. Danach müssen nachgelagerte Prüfungen und API-/UI-Abbildungen angepasst werden. Bei einer Änderung am Schema muss der dateiinhaltsbasierte Cache berücksichtigt werden: Alter Dateiinhalt kann weiterhin alte Extraktionsdaten liefern.

## Wichtige Grenzen des aktuellen Codes

| Bereich | Grenze |
|---|---|
| Steuerliche Felder | Leistungsdatum nicht extrahiert/geprüft; Reverse-Charge-Prüfung vereinfacht |
| Datenqualität | Nicht jedes fehlende Feld blockiert; einige Rechenprüfungen werden ausgelassen |
| Grounding | Textsuche ohne semantische Feldzuordnung; ohne Textschicht übersprungen |
| Cache | Modell-, Prompt- und Schemaversion nicht im Cache-Schlüssel |
| Persistenz | JSON-Dateien ohne Transaktionen und Sperren; wiederholtes Anhängen möglich |
| Manuelle Entscheidung | Override nach Dokument-ID, keine unveränderliche Änderungshistorie |
| Mehrbenutzerbetrieb | Keine Benutzerverwaltung; parallele Schreibzugriffe nicht abgesichert |
| Datenvertrag | Begrenzte Requestvalidierung; einige Frontend-Defaults stammen aus dem Mock-Adapter |

Die konkreten Auswirkungen sind in [Prüfkatalog](pruefregeln.md), [Ledger](ledger.md), [API](api.md) und [Frontend](frontend.md) erläutert. Diese Punkte beschreiben den untersuchten Stand; im Zuge dieser Dokumentation wurden keine Anwendungsfunktionen geändert.

## Quellen

`eval/eval.py`, `eval/generate_synthetic_set.py`, `eval/generate_injection_demo.py`, `README.md` sowie die in den Fachkapiteln genannten Quelldateien.

[Zur Übersicht](overview.md)
