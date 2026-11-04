"""
Erzeugt ein kleines, synthetisches Set unbekannter Belege (nicht Teil der
16 Original-Testbelege), um zu zeigen, dass der Skill nicht auf die 16
auswendig gelernten Fälle überfit ist, sondern echte Regeln anwendet.

Aufruf: python eval/generate_synthetic_set.py
Erzeugt: eval/synthetic/*.pdf + eval/synthetic/ground_truth.csv
"""
import csv
import os

import pymupdf

OUT_DIR = os.path.join(os.path.dirname(__file__), "synthetic")
os.makedirs(OUT_DIR, exist_ok=True)

BLACK = (0, 0, 0)


def make_pdf(filename: str, lines: list[tuple[int, int, str, int]]) -> None:
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    for x, y, text, size in lines:
        page.insert_text((x, y), text, fontsize=size, color=BLACK)
    doc.save(os.path.join(OUT_DIR, filename))
    doc.close()


ground_truth: list[dict] = []


def add_gt(doc_id: str, expected: str, expected_checks: str, note: str) -> None:
    ground_truth.append({"doc_id": doc_id, "erwartete_entscheidung": expected, "erwartete_check_ids": expected_checks, "notiz": note})


# S1: sauberer, bisher ungesehener Beleg zu einer echten Bestellung -> freigeben
make_pdf("s01_clean_new_invoice.pdf", [
    (72, 72, "Fruchtkontor Bodensee GmbH", 12),
    (72, 90, "Lindau", 10),
    (72, 130, "Rechnung", 16),
    (72, 155, "Rechnungsnr. RE-7001", 10),
    (72, 170, "Datum: 2026-08-11", 10),
    (72, 185, "Ihre Bestellnr.: QB-10416", 10),
    (72, 215, "Rechnungssteller", 10),
    (72, 230, "Fruchtkontor Bodensee GmbH, Lindau", 10),
    (72, 245, "Steuernr.: DE 299 114 552", 10),
    (72, 275, "Rechnungsempfänger", 10),
    (72, 290, "Quellberg GmbH, Getränkemanufaktur", 10),
    (72, 305, "Limonadenweg 3, 94032 Passau", 10),
    (72, 340, "Pos  Bezeichnung                              Menge  Einzelpreis   Gesamt", 9),
    (72, 358, "1    Apfelsaftkonzentrat 70 Brix IBC          8      1240,00       9.920,00", 9),
    (72, 390, "Nettobetrag                                                 € 9.920,00", 10),
    (72, 405, "zzgl. 7% USt                                                € 694,40", 10),
    (72, 420, "Gesamtbetrag brutto                                         € 10.614,40", 10),
    (72, 455, "Fruchtkontor Bodensee GmbH · Lindau", 9),
    (72, 470, "IBAN: DE89370400440532013000", 9),
])
add_gt("s01_clean_new_invoice", "freigeben", "", "Sauberer, unbekannter Beleg zu echter Bestellung - Generalisierungstest.")

# S2: Zahlungserinnerung (Mahnung) statt Rechnung -> hinschauen (A3)
make_pdf("s02_mahnung.pdf", [
    (72, 72, "Kronkorken Müller KG", 12),
    (72, 90, "Augsburg", 10),
    (72, 130, "Zahlungserinnerung", 16),
    (72, 155, "Zu Rechnung RE-5567", 10),
    (72, 170, "Datum: 2026-08-20", 10),
    (72, 200, "Sehr geehrte Damen und Herren,", 10),
    (72, 220, "wir bitten um Ausgleich des offenen Betrags von € 5.414,50", 10),
    (72, 235, "innerhalb von 7 Tagen. Dies ist keine Rechnung.", 10),
    (72, 280, "Kronkorken Müller KG · Augsburg", 9),
])
add_gt("s02_mahnung", "hinschauen", "A3", "Mahnung, keine Rechnung - darf nie automatisch freigegeben werden.")

# S3: Gutschrift statt Rechnung -> hinschauen (A3)
make_pdf("s03_gutschrift.pdf", [
    (72, 72, "Kartonagen Beck GmbH", 12),
    (72, 90, "Straubing", 10),
    (72, 130, "Gutschrift", 16),
    (72, 155, "Gutschrift-Nr. GS-331", 10),
    (72, 170, "Datum: 2026-08-15", 10),
    (72, 185, "Bezug: Bestellnr. QB-10398", 10),
    (72, 220, "Pos  Bezeichnung                      Menge  Einzelpreis   Gesamt", 9),
    (72, 238, "1    Gutschrift Transportschaden      100    0,62          62,00", 9),
    (72, 270, "Gutschriftsbetrag netto                             € 62,00", 10),
    (72, 285, "zzgl. 19% USt                                        € 11,78", 10),
    (72, 300, "Gesamtbetrag                                         € 73,78", 10),
    (72, 335, "Kartonagen Beck GmbH · Straubing", 9),
])
add_gt("s03_gutschrift", "hinschauen", "A3", "Gutschrift, keine Rechnung.")

# S4: falsche USt-Berechnung -> hinschauen (C4)
make_pdf("s04_vat_error.pdf", [
    (72, 72, "Brauereibedarf Hartmann GmbH", 12),
    (72, 90, "Freising", 10),
    (72, 130, "Rechnung", 16),
    (72, 155, "Rechnungsnr. RE-8841-B", 10),
    (72, 170, "Datum: 2026-08-05", 10),
    (72, 215, "Rechnungssteller", 10),
    (72, 230, "Brauereibedarf Hartmann GmbH, Freising", 10),
    (72, 245, "Steuernr.: DE 188 220 441", 10),
    (72, 275, "Rechnungsempfänger", 10),
    (72, 290, "Quellberg GmbH, Getränkemanufaktur", 10),
    (72, 305, "Limonadenweg 3, 94032 Passau", 10),
    (72, 340, "Pos  Bezeichnung                       Menge  Einzelpreis   Gesamt", 9),
    (72, 358, "1    CO2-Flaschen Füllung 10kg         50     18,00         900,00", 9),
    (72, 390, "Nettobetrag                                          € 900,00", 10),
    (72, 405, "zzgl. 19% USt                                        € 110,00", 10),  # korrekt waeren 171,00
    (72, 420, "Gesamtbetrag brutto                                  € 1.010,00", 10),
    (72, 455, "Brauereibedarf Hartmann GmbH · Freising", 9),
    (72, 470, "IBAN: DE89370400440532013000", 9),
])
add_gt("s04_vat_error", "hinschauen", "C4", "USt falsch berechnet (110 statt 171 EUR bei 19% auf 900 EUR).")

# S5: manipulierte IBAN (eine Ziffer geaendert) -> hinschauen (E4)
make_pdf("s05_iban_tampered.pdf", [
    (72, 72, "Hopfen & Etikett Druck GmbH", 12),
    (72, 90, "Wolnzach", 10),
    (72, 130, "Rechnung", 16),
    (72, 155, "Rechnungsnr. RE-3391", 10),
    (72, 170, "Datum: 2026-08-18", 10),
    (72, 215, "Rechnungssteller", 10),
    (72, 230, "Hopfen & Etikett Druck GmbH, Wolnzach", 10),
    (72, 245, "Steuernr.: DE 147 998 221", 10),
    (72, 275, "Rechnungsempfänger", 10),
    (72, 290, "Quellberg GmbH, Getränkemanufaktur", 10),
    (72, 305, "Limonadenweg 3, 94032 Passau", 10),
    (72, 340, "Pos  Bezeichnung                       Menge  Einzelpreis   Gesamt", 9),
    (72, 358, "1    Etiketten Hopfenaroma, matt       5000   0,137         685,00", 9),
    (72, 390, "Nettobetrag                                          € 685,00", 10),
    (72, 405, "zzgl. 19% USt                                        € 130,15", 10),
    (72, 420, "Gesamtbetrag brutto                                  € 815,15", 10),
    (72, 455, "Hopfen & Etikett Druck GmbH · Wolnzach", 9),
    (72, 470, "IBAN: DE89370400440532013099", 9),  # letzte Ziffern manipuliert -> ungueltige Pruefsumme
])
add_gt("s05_iban_tampered", "hinschauen", "E4", "IBAN-Pruefsumme ungueltig (letzte Ziffern manipuliert).")

# S6: englisches Zahlenformat, ansonsten sauber -> freigeben (kein falscher Alarm)
make_pdf("s06_english_format.pdf", [
    (72, 72, "Glashütte Weiden GmbH", 12),
    (72, 90, "Weiden", 10),
    (72, 130, "Invoice", 16),
    (72, 155, "Invoice No. INV-2026-998", 10),
    (72, 170, "Date: 2026-08-22", 10),
    (72, 185, "Your order no.: QB-10391", 10),
    (72, 215, "Supplier", 10),
    (72, 230, "Glashuette Weiden GmbH, Weiden", 10),
    (72, 245, "VAT-ID: DE 229 884 112", 10),
    (72, 275, "Bill to", 10),
    (72, 290, "Quellberg GmbH, Getraenkemanufaktur", 10),
    (72, 305, "Limonadenweg 3, 94032 Passau", 10),
    (72, 340, "Pos  Description                       Qty   Unit price   Amount", 9),
    (72, 358, "1    Longneck bottle 0.33l clear (plt)  20    212.50       4,250.00", 9),
    (72, 390, "Net amount                                        EUR 4,250.00", 10),
    (72, 405, "plus 19% VAT                                      EUR 807.50", 10),
    (72, 420, "Total amount gross                                EUR 5,057.50", 10),
    (72, 455, "Glashuette Weiden GmbH - Weiden", 9),
    (72, 470, "IBAN: DE89370400440532013000", 9),
])
add_gt("s06_english_format", "freigeben", "", "Englisches Zahlenformat (1,500.00) - darf keinen falschen Alarm ausloesen.")

gt_path = os.path.join(OUT_DIR, "ground_truth.csv")
with open(gt_path, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["doc_id", "erwartete_entscheidung", "erwartete_check_ids", "notiz"], delimiter=";")
    writer.writeheader()
    writer.writerows(ground_truth)

print(f"{len(ground_truth)} synthetische Belege erzeugt in {OUT_DIR}")
print(f"Ground truth: {gt_path}")
