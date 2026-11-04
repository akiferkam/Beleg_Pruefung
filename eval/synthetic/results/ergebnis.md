# Ergebnis Beleg-Prüfung

Erzeugt: 2026-11-04T13:49:16.694719+00:00


**2 freigeben / 4 hinschauen** von 6 Belegen.


## Übersicht

| Beleg | Entscheidung | Lieferant | Rechnungsnr. | Betrag brutto | Bestellnr. |
|---|---|---|---|---|---|
| s01_clean_new_invoice | **freigeben** | Fruchtkontor Bodensee GmbH | RE-7001 | 10614.4 | QB-10416 |
| s02_mahnung | **hinschauen** | Kronkorken Müller KG | RE-5567 | 5414.5 | - |
| s03_gutschrift | **hinschauen** | Kartonagen Beck GmbH | GS-331 | 73.78 | QB-10398 |
| s04_vat_error | **hinschauen** | Brauereibedarf Hartmann GmbH | RE-8841-B | 1010.0 | - |
| s05_iban_tampered | **hinschauen** | Hopfen & Etikett Druck GmbH | RE-3391 | 815.15 | - |
| s06_english_format | **freigeben** | Glashuette Weiden GmbH | INV-2026-998 | 5057.5 | QB-10391 |

## Details


### s01_clean_new_invoice — FREIGEBEN

- Lieferant: Fruchtkontor Bodensee GmbH
- Rechnungsnr.: RE-7001
- Betrag brutto: 10614.4
- Bestellnummer: QB-10416
- Zur Information (nicht blockierend):
  - [A1] Datei konnte geöffnet und gelesen werden.
  - [A2] Kernfelder (Beträge, Lieferant, Rechnungsnummer) wurden lesbar extrahiert.
  - [A3] Belegtyp: Rechnung.
  - [A4] Seitenzahl stimmt (1/1).
  - [A5] Alle geprüften Beträge/Mengen (4) im Rohtext wiedergefunden.
  - [B1] Rechnungsempfänger korrekt: Quellberg GmbH, Getränkemanufaktur, Limonadenweg 3, 94032 Passau.
  - [B2] Lieferant vollständig angegeben: Fruchtkontor Bodensee GmbH, Lindau.
  - [B3] Steuernummer des Lieferanten vorhanden: DE 299 114 552.
  - [B4] Rechnungsnummer RE-7001, Datum 2026-08-11 plausibel.
  - [B5] Netto, USt-Satz, USt-Betrag und Brutto sind ausgewiesen.
  - [B6] Kein 0%-Fall, Prüfung entfällt.
  - [B7] Leistungsdatum wird aktuell nicht geprüft (bewusste Scope-Entscheidung, siehe README).
  - [C1] Positions-Arithmetik korrekt (1 Position(en) geprüft, Toleranz 0.005 €/Einheit für gerundete Anzeigepreise).
  - [C2] Summe der Positionen (9920.00 €) stimmt mit Nettobetrag (9920.00 €) überein.
  - [C3] USt-Satz 7% ist gültig.
  - [C4] USt-Betrag korrekt: 9920.00 € × 7% = 694.40 €.
  - [C5] Brutto korrekt: 9920.00 € + 694.40 € = 10614.40 €.
  - [C6] Währung EUR, Betrag positiv.
  - [D1] Bestellnummer im Beleg angegeben: QB-10416.
  - [D2] Bestellnummer QB-10416 in bestellungen.csv gefunden (Fruchtkontor Bodensee GmbH, Apfelsaftkonzentrat 70 Brix IBC).
  - [D3] Lieferant passt zur Bestellung (100% Ähnlichkeit).
  - [D4] Einzelpreis(e) stimmen mit Bestellpreis 1240.0 € überein.
  - [D5] Kumulativ in Rechnung gestellte Menge (8) liegt innerhalb der bestellten Menge (8).
  - [D6] Keine zusätzlichen, nicht bestellten Positionen.
  - [D7] Keine Rahmenbestellung.
  - [E1] Datei-Hash wurde noch nicht verarbeitet.
  - [E2] Keine Dopplung von Lieferant + Rechnungsnummer im Ledger.
  - [E3] Kein inhaltliches Duplikat im Ledger gefunden.
  - [E4] IBAN-Prüfsumme gültig: DE89370400440532013000.
  - [E5] Erste bekannte Rechnung dieses Lieferanten - keine Historie zum Abgleich.
  - [E6] Keine an ein Prüfsystem gerichtete Formulierung im Dokument gefunden.
  - [F1] Rechnungsbetrag 10614.40 € unterhalb der Freigabegrenze von 50000.00 €.
  - [F2] Kein Skonto-Hinweis im Beleg.

### s02_mahnung — HINSCHAUEN

- Lieferant: Kronkorken Müller KG
- Rechnungsnr.: RE-5567
- Betrag brutto: 5414.5
- Bestellnummer: -
- Gründe:
  - [A3] Beleg ist keine Rechnung, sondern: Mahnung. Im Dokument: „Dies ist keine Rechnung.“. Keine Zahlungsfreigabe ohne Rechnung möglich.
- Zur Information (nicht blockierend):
  - [A1] Datei konnte geöffnet und gelesen werden.
  - [A2] Kernfelder (Beträge, Lieferant, Rechnungsnummer) wurden lesbar extrahiert.
  - [A4] Keine Seitenangabe im Dokument (z.B. 'Seite 1 von N') - Prüfung entfällt.
  - [A5] Alle geprüften Beträge/Mengen (1) im Rohtext wiedergefunden.

### s03_gutschrift — HINSCHAUEN

- Lieferant: Kartonagen Beck GmbH
- Rechnungsnr.: GS-331
- Betrag brutto: 73.78
- Bestellnummer: QB-10398
- Gründe:
  - [A3] Beleg ist keine Rechnung, sondern: Gutschrift. Keine Zahlungsfreigabe ohne Rechnung möglich.
- Zur Information (nicht blockierend):
  - [A1] Datei konnte geöffnet und gelesen werden.
  - [A2] Kernfelder (Beträge, Lieferant, Rechnungsnummer) wurden lesbar extrahiert.
  - [A4] Seitenzahl stimmt (1/1).
  - [A5] Alle geprüften Beträge/Mengen (5) im Rohtext wiedergefunden.

### s04_vat_error — HINSCHAUEN

- Lieferant: Brauereibedarf Hartmann GmbH
- Rechnungsnr.: RE-8841-B
- Betrag brutto: 1010.0
- Bestellnummer: -
- Gründe:
  - [C4] USt-Betrag stimmt nicht: 900.00 € × 19% = 171.00 €, Rechnung sagt 110.00 € (Differenz 61.00 €).
  - [D1] Keine Bestellnummer im Beleg - ohne Bestellbezug kann nicht geprüft werden, ob Ware/Leistung je bestellt wurde.
- Zur Information (nicht blockierend):
  - [A1] Datei konnte geöffnet und gelesen werden.
  - [A2] Kernfelder (Beträge, Lieferant, Rechnungsnummer) wurden lesbar extrahiert.
  - [A3] Belegtyp: Rechnung.
  - [A4] Seitenzahl stimmt (1/1).
  - [A5] Alle geprüften Beträge/Mengen (5) im Rohtext wiedergefunden.
  - [B1] Rechnungsempfänger korrekt: Quellberg GmbH, Getränkemanufaktur, Limonadenweg 3, 94032 Passau.
  - [B2] Lieferant vollständig angegeben: Brauereibedarf Hartmann GmbH, Freising.
  - [B3] Steuernummer des Lieferanten vorhanden: DE 188 220 441.
  - [B4] Rechnungsnummer RE-8841-B, Datum 2026-08-05 plausibel.
  - [B5] Netto, USt-Satz, USt-Betrag und Brutto sind ausgewiesen.
  - [B6] Kein 0%-Fall, Prüfung entfällt.
  - [B7] Leistungsdatum wird aktuell nicht geprüft (bewusste Scope-Entscheidung, siehe README).
  - [C1] Positions-Arithmetik korrekt (1 Position(en) geprüft, Toleranz 0.005 €/Einheit für gerundete Anzeigepreise).
  - [C2] Summe der Positionen (900.00 €) stimmt mit Nettobetrag (900.00 €) überein.
  - [C3] USt-Satz 19% ist gültig.
  - [C5] Brutto korrekt: 900.00 € + 110.00 € = 1010.00 €.
  - [C6] Währung EUR, Betrag positiv.
  - [D2] Keine Bestellnummer angegeben - Prüfung entfällt (siehe D1).
  - [E1] Datei-Hash wurde noch nicht verarbeitet.
  - [E2] Keine Dopplung von Lieferant + Rechnungsnummer im Ledger.
  - [E3] Kein inhaltliches Duplikat im Ledger gefunden.
  - [E4] IBAN-Prüfsumme gültig: DE89370400440532013000.
  - [E5] Erste bekannte Rechnung dieses Lieferanten - keine Historie zum Abgleich.
  - [E6] Keine an ein Prüfsystem gerichtete Formulierung im Dokument gefunden.
  - [F1] Rechnungsbetrag 1010.00 € unterhalb der Freigabegrenze von 50000.00 €.
  - [F2] Kein Skonto-Hinweis im Beleg.

### s05_iban_tampered — HINSCHAUEN

- Lieferant: Hopfen & Etikett Druck GmbH
- Rechnungsnr.: RE-3391
- Betrag brutto: 815.15
- Bestellnummer: -
- Gründe:
  - [D1] Keine Bestellnummer im Beleg - ohne Bestellbezug kann nicht geprüft werden, ob Ware/Leistung je bestellt wurde.
  - [E4] IBAN-Prüfsumme ungültig: DE89370400440532013099.
- Zur Information (nicht blockierend):
  - [A1] Datei konnte geöffnet und gelesen werden.
  - [A2] Kernfelder (Beträge, Lieferant, Rechnungsnummer) wurden lesbar extrahiert.
  - [A3] Belegtyp: Rechnung.
  - [A4] Seitenzahl stimmt (1/1).
  - [A5] Alle geprüften Beträge/Mengen (5) im Rohtext wiedergefunden.
  - [B1] Rechnungsempfänger korrekt: Quellberg GmbH, Getränkemanufaktur, Limonadenweg 3, 94032 Passau.
  - [B2] Lieferant vollständig angegeben: Hopfen & Etikett Druck GmbH, Wolnzach.
  - [B3] Steuernummer des Lieferanten vorhanden: DE 147 998 221.
  - [B4] Rechnungsnummer RE-3391, Datum 2026-08-18 plausibel.
  - [B5] Netto, USt-Satz, USt-Betrag und Brutto sind ausgewiesen.
  - [B6] Kein 0%-Fall, Prüfung entfällt.
  - [B7] Leistungsdatum wird aktuell nicht geprüft (bewusste Scope-Entscheidung, siehe README).
  - [C1] Positions-Arithmetik korrekt (1 Position(en) geprüft, Toleranz 0.005 €/Einheit für gerundete Anzeigepreise).
  - [C2] Summe der Positionen (685.00 €) stimmt mit Nettobetrag (685.00 €) überein.
  - [C3] USt-Satz 19% ist gültig.
  - [C4] USt-Betrag korrekt: 685.00 € × 19% = 130.15 €.
  - [C5] Brutto korrekt: 685.00 € + 130.15 € = 815.15 €.
  - [C6] Währung EUR, Betrag positiv.
  - [D2] Keine Bestellnummer angegeben - Prüfung entfällt (siehe D1).
  - [E1] Datei-Hash wurde noch nicht verarbeitet.
  - [E2] Keine Dopplung von Lieferant + Rechnungsnummer im Ledger.
  - [E3] Kein inhaltliches Duplikat im Ledger gefunden.
  - [E5] Erste bekannte Rechnung dieses Lieferanten - keine Historie zum Abgleich.
  - [E6] Keine an ein Prüfsystem gerichtete Formulierung im Dokument gefunden.
  - [F1] Rechnungsbetrag 815.15 € unterhalb der Freigabegrenze von 50000.00 €.
  - [F2] Kein Skonto-Hinweis im Beleg.

### s06_english_format — FREIGEBEN

- Lieferant: Glashuette Weiden GmbH
- Rechnungsnr.: INV-2026-998
- Betrag brutto: 5057.5
- Bestellnummer: QB-10391
- Zur Information (nicht blockierend):
  - [A1] Datei konnte geöffnet und gelesen werden.
  - [A2] Kernfelder (Beträge, Lieferant, Rechnungsnummer) wurden lesbar extrahiert.
  - [A3] Belegtyp: Rechnung.
  - [A4] Seitenzahl stimmt (1/1).
  - [A5] Alle geprüften Beträge/Mengen (5) im Rohtext wiedergefunden.
  - [B1] Rechnungsempfänger korrekt: Quellberg GmbH, Getraenkemanufaktur, Limonadenweg 3, 94032 Passau.
  - [B2] Lieferant vollständig angegeben: Glashuette Weiden GmbH, Weiden.
  - [B3] USt-IdNr des Lieferanten vorhanden: DE 229 884 112.
  - [B4] Rechnungsnummer INV-2026-998, Datum 2026-08-22 plausibel.
  - [B5] Netto, USt-Satz, USt-Betrag und Brutto sind ausgewiesen.
  - [B6] Kein 0%-Fall, Prüfung entfällt.
  - [B7] Leistungsdatum wird aktuell nicht geprüft (bewusste Scope-Entscheidung, siehe README).
  - [C1] Positions-Arithmetik korrekt (1 Position(en) geprüft, Toleranz 0.005 €/Einheit für gerundete Anzeigepreise).
  - [C2] Summe der Positionen (4250.00 €) stimmt mit Nettobetrag (4250.00 €) überein.
  - [C3] USt-Satz 19% ist gültig.
  - [C4] USt-Betrag korrekt: 4250.00 € × 19% = 807.50 €.
  - [C5] Brutto korrekt: 4250.00 € + 807.50 € = 5057.50 €.
  - [C6] Währung EUR, Betrag positiv.
  - [D1] Bestellnummer im Beleg angegeben: QB-10391.
  - [D2] Bestellnummer QB-10391 in bestellungen.csv gefunden (Glashütte Weiden GmbH, Longneck-Flasche 0,33l klar (Palette)).
  - [D3] Lieferant passt zur Bestellung (93% Ähnlichkeit).
  - [D4] Einzelpreis(e) stimmen mit Bestellpreis 212.5 € überein.
  - [D5] Kumulativ in Rechnung gestellte Menge (20) liegt innerhalb der bestellten Menge (96).
  - [D6] Keine zusätzlichen, nicht bestellten Positionen.
  - [D7] Keine Rahmenbestellung.
  - [E1] Datei-Hash wurde noch nicht verarbeitet.
  - [E2] Keine Dopplung von Lieferant + Rechnungsnummer im Ledger.
  - [E3] Kein inhaltliches Duplikat im Ledger gefunden.
  - [E4] IBAN-Prüfsumme gültig: DE89370400440532013000.
  - [E5] Erste bekannte Rechnung dieses Lieferanten - keine Historie zum Abgleich.
  - [E6] Keine an ein Prüfsystem gerichtete Formulierung im Dokument gefunden.
  - [F1] Rechnungsbetrag 5057.50 € unterhalb der Freigabegrenze von 50000.00 €.
  - [F2] Kein Skonto-Hinweis im Beleg.
