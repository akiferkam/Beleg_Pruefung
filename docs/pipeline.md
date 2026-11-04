# Pipeline und Extraktion

`scripts/pipeline.py::process_folder` ist der gemeinsame Verarbeitungskern. CLI und API unterscheiden sich vor allem bei Eingabeparametern, Speicherung und Präsentation.

## Ablauf

1. Modellkonfiguration, Bestellungen und persistentes Ledger laden.
2. Mit `find_belege` direkte Dateien des Ordners alphabetisch sammeln; CSV-Dateien ausnehmen.
3. Jede Datei über `intake.load_document` öffnen und ihren SHA-256-Hash berechnen.
4. Für lesbare Dateien eine gecachte Extraktion laden oder Vision aufrufen.
5. Die Datensätze nach extrahiertem Rechnungsdatum sortieren; Dokumente ohne Datum folgen danach. `doc_id` dient als weiteres Sortierkriterium.
6. Extraktionswerte gegen die vorhandene Textschicht abgleichen, Prüfungen ausführen und Entscheidung bilden.
7. Für jede vorhandene Extraktion einen Ledger-Eintrag im Arbeitsspeicher ergänzen, auch bei `hinschauen`.
8. Das Ledger nur bei `commit_to_ledger=True` speichern.

Die Reihenfolge beeinflusst Mengen- und Duplikatprüfungen. Ein späteres Dokument sieht bereits die zuvor im selben Lauf erfassten Einträge.

## Interne Datenmodelle

| Typ | Wichtige Felder |
|---|---|
| `PageContent` | PNG-Seitenbild und vorhandener digitaler Text |
| `IntakeResult` | `doc_id`, Dateipfad, Typ, Seiten, Lesbarkeit, Fehler |
| `ProcessedDoc` | Aufnahme, Hash, Extraktion, Fehler, Befunde, Entscheidung und Zusatzkontext |
| `GroundingReport` | Übersprungen-Status, geprüfte und nicht wiedergefundene Felder |

`doc_id` ist der Dateiname ohne Endung. Gleiche Dateistämme in verschiedenen Ordnern oder Dateiformaten erhalten dadurch dieselbe ID.

## Dateiaufnahme

PDFs werden mit PyMuPDF geöffnet und mit 200 DPI gerendert. Pillow reduziert die längste Bildkante bei Bedarf auf 1.600 Pixel. Eine vorhandene Textschicht wird separat extrahiert. Passwortgeschützte PDFs werden zunächst mit leerem Passwort versucht; andernfalls entsteht ein Lesefehler.

Die Bild-Endungsliste enthält JPG/JPEG, PNG, TIF/TIFF, WEBP und HEIC. Die tatsächliche Dekodierung hängt von Pillow und verfügbaren Formaten ab. Bei Bildern wird nur das geladene Bild in eine Seite überführt; mehrere TIFF-Frames werden nicht durchlaufen. Eine OCR-Textschicht erzeugt diese Stufe nicht.

Nicht unterstützte direkte Dateien werden ebenfalls aufgenommen und führen zu einem A1-Befund. Unterordner werden nicht durchsucht. Ein nicht behandelter Fehler beim Datei-Hash oder beim Laden einer beschädigten Cache-Datei kann dagegen den gesamten Lauf abbrechen.

## Vision-Extraktion

`extract.py` sendet Seitenbilder als Base64-PNGs und ergänzend den digitalen Text an `Anthropic.messages.create`. Ein erzwungener Tool-Aufruf `submit_beleg_extraction` liefert die Rohdaten.

Das Schema enthält unter anderem Belegtyp, Lieferant, Empfänger, Rechnungsnummer und -datum, Bestellreferenz, Positionen, Netto/USt/Brutto, Bankverbindung, Reverse-Charge-Signale und `manipulation_attempt`. Nicht sicher lesbare Werte sollen `null` sein.

Der Systemprompt behandelt Dokumenttext als Daten und fordert bei anweisungsartigen Texten ein Zitat im Manipulationsfeld. Der Python-Code übernimmt daraus keine direkte Freigabe. `extract_document_safe` fängt Ausnahmen des Extraktionsaufrufs ab und liefert einen Fehlertext für A2. Eine separate umfassende lokale Schema-Validierung des zurückgegebenen `block.input` findet in dieser Funktion nicht statt.

## Cache

Der Cache liegt normalerweise unter `.cache/extracted/<sha256>.json`. Eine Regeländerung kann deshalb dieselben Rohdaten ohne erneuten Modellaufruf auswerten. Der Schlüssel berücksichtigt ausschließlich den Dateiinhalt, nicht Modell, Prompt, Schema oder Konfiguration.

CLI `--no-cache` setzt das Cache-Verzeichnis für diesen Lauf auf `None`. Der Web-Endpunkt bietet keinen entsprechenden Schalter. `results/extracted/<doc_id>.json` sind dagegen Ergebnis-Kopien und werden nicht als Hash-Cache gelesen.

## Grounding

`normalize.check_grounding` sucht mehrere deutsche und englische Zahlendarstellungen im normalisierten Text. Geprüft werden Netto-, Steuer- und Bruttobetrag sowie Positionsmengen und Positionssummen. Einstellige ganze Zahlen mit Betrag kleiner 10 werden als zu unspezifisch ausgelassen.

Fehlt digitaler Text, wird die Prüfung als übersprungen behandelt. Sie ist ein textueller Plausibilitätsabgleich; sie weist einem Betrag keine bestimmte semantische Stelle im Dokument zu. Obwohl `config.yaml` ein Feld `grounding_enabled` enthält, fragt der untersuchte Pipeline-Aufruf dieses Feld nicht ab.

## Quellen

`scripts/pipeline.py`, `scripts/intake.py`, `scripts/extract.py`, `scripts/normalize.py`.

[Zur Übersicht](overview.md) · [Prüfkatalog](pruefregeln.md)
