# Prüfkatalog und automatische Entscheidung

`checks.run_all_checks` erstellt `Finding`-Objekte mit `check_id`, `level`, `passed`, `message` und `policy_tunable`. Ein Befund blockiert genau dann, wenn `level == "BLOCK"` und `passed == False` gilt. `decide.decide` setzt bei mindestens einem blockierenden Befund `hinschauen`, ansonsten `freigeben`.

## Ausführungsreihenfolge

A1 und A2 werden zuerst geprüft. Schlägt einer fehl, endet die Prüfung dieses Dokuments. Danach folgen A3, A4 und A5. Ist das Dokument keine Rechnung, endet der weitere Katalog nach diesen Prüfungen. Fehler in A4 oder A5 verhindern dagegen nicht die anschließenden B–F-Prüfungen einer Rechnung.

## A: Lesbarkeit und Format

| ID | Implementiertes Verhalten |
|---|---|
| A1 | Datei konnte geöffnet und aufgenommen werden |
| A2 | Extraktion vorhanden, kein Extraktionsfehler und kein Unlesbarkeitsflag |
| A3 | `document_type` ist exakt `Rechnung` |
| A4 | Behauptete Gesamtseitenzahl entspricht der gelieferten Seitenzahl; ohne Angabe entfällt der Vergleich |
| A5 | Geprüfte Zahlen sind in der digitalen Textschicht wiederzufinden; ohne Textschicht übersprungen |

## B: Formale Angaben

| ID | Implementiertes Verhalten |
|---|---|
| B1 | Erstes Wort des konfigurierten Firmennamens im Empfängernamen und konfigurierte Adressfragmente vorhanden |
| B2 | Name und Adresse des Lieferanten vorhanden |
| B3 | Lieferanten-Steuerkennung und ein bekannter Kennungstyp vorhanden |
| B4 | Rechnungsnummer sowie ISO-Datum vorhanden; Datum nicht in der Zukunft |
| B5 | Netto, USt-Satz, USt-Betrag und Brutto nicht `None` |
| B6 | Bei 0 %: Reverse-Charge-Hinweis und Steuerkennungen von Empfänger und Lieferant vorhanden |
| B7 | Leistungsdatum wird als Information ausdrücklich nicht geprüft |

B6 vergleicht die Empfängerkennung trotz übergebenem Konfigurationswert nicht mit der Firmen-USt-ID. Jeder 0%-Fall wird auf die genannten Reverse-Charge-Angaben geprüft; andere steuerliche Gründe für 0 % werden nicht gesondert modelliert. Die Dokumentation beschreibt diese Regeln, ohne daraus eine vollständige steuerrechtliche Prüfung abzuleiten.

## C: Arithmetik

| ID | Implementiertes Verhalten |
|---|---|
| C1 | Je vollständiger Position: `abs(Menge * Einzelpreis - Positionssumme) <= abs(Menge) * Toleranz` |
| C2 | Summe vorhandener Positionssummen gegen Netto; bei unzureichenden Daten INFO |
| C3 | USt-Satz in der konfigurierten Liste; fehlender Satz wird bereits in B5 behandelt |
| C4 | `Netto * USt-Satz / 100` gegen USt-Betrag |
| C5 | `Netto + USt` gegen Brutto |
| C6 | Eine angegebene Währung muss EUR sein; ein vorhandenes Brutto muss positiv sein |

C1 lässt Positionen mit fehlenden Operanden aus. C6 blockiert eine leere Währung nicht. Die Berechnungen verwenden Python-Fließkommazahlen und absolute Toleranzen.

## D: Bestellabgleich

| ID | Implementiertes Verhalten |
|---|---|
| D1 | Fehlende Bestellreferenz je nach Policy BLOCK oder INFO |
| D2 | Angegebene Referenz muss in der CSV existieren; unbekannte Referenz bleibt unabhängig von D1 blockierend |
| D3 | Lieferantenvergleich mit RapidFuzz `token_set_ratio`, Standardschwelle 70 |
| D4 | Einzelpreise zugeordneter Positionen gegen Bestellpreis |
| D5 | Bereits erfasste Menge plus aktuelle passende Menge darf Bestellmenge nicht überschreiten |
| D6 | Wert zusätzlicher Positionen im Verhältnis zum Bestellwert |
| D7 | Information über Rahmenbestellung |

D3–D7 werden nur bei gefundener Bestellung ausgeführt. Positionen zählen ab einem fest im Code definierten Fuzzy-Score von 40 als passend. Ein Bestell-Einzelpreis von 0 kennzeichnet einen Rahmenvertrag; D4 und D5 entfallen dann. Zusatzpositionen bei einem Referenzwert kleiner oder gleich 0 bleiben manuell zu prüfen. Gleiche Rechnungsnummern werden bei der historischen Mengenberechnung ausgeschlossen.

## E: Duplikate und Auffälligkeiten

| ID | Implementiertes Verhalten |
|---|---|
| E1 | Identischer Datei-Hash bereits im Ledger |
| E2 | Gleicher normalisierter Lieferantenname und gleiche Rechnungsnummer |
| E3 | Gleicher Positionsfingerabdruck und kompatibler Bruttobetrag unter anderer Rechnungsnummer |
| E4 | Vorhandene IBAN hat eine gültige Modulo-97-Prüfsumme |
| E5 | Vorhandene IBAN stimmt mit einer bekannten IBAN des Lieferanten überein |
| E6 | Extrahiertes Manipulationszitat führt zu einem blockierenden Befund |

Fehlende IBAN oder fehlende Bankhistorie werden als INFO behandelt. E3 filtert nicht zusätzlich auf Lieferant oder Bestellnummer. E6 hängt davon ab, ob die Extraktion einen Versuch erfasst.

## F: Geschäftsregeln

F1 blockiert, wenn das Brutto **größer** als die Freigabegrenze ist; Gleichheit blockiert hier nicht. F2 zeigt vorhandene Skontobedingungen nur als Information an.

## Standardwerte aus `config.yaml`

| Policy | Wert |
|---|---:|
| Zusatzpositionen | 10 % des Bestellwerts |
| Bestellbezug erforderlich | `true` |
| Obligatorische Prüfung oberhalb | 50.000 € brutto |
| Positionsarithmetik je Einheit | 0,005 € |
| Nettosumme | 0,05 € |
| USt-Betrag / Bruttobetrag | jeweils 0,02 € |
| USt-Sätze | 0, 7, 19 |
| Lieferanten-Fuzzy-Score | 70 |

## Quellen

`scripts/checks/base.py`, sämtliche Dateien in `scripts/checks/`, `scripts/decide.py`, `config.yaml`.

[Zur Übersicht](overview.md) · [Ledger und Berichte](ledger.md)
