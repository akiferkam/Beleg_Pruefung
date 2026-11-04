"""
Vergleicht die tatsächlichen Entscheidungen des Skills mit einer
Ground-Truth-CSV und gibt eine Konfusionsmatrix + die wichtigste Kennzahl aus:
false_freigeben (Ground Truth = hinschauen, System = freigeben) MUSS 0 sein -
das wäre ein Fehler, der Geld kostet. false_hinschauen (umgekehrt) ist der
Preis an unnötiger manueller Arbeit, aber ungefährlich.

Aufruf:
    python eval/eval.py --ergebnis results/ergebnis.csv --ground-truth eval/ground_truth.csv
    python eval/eval.py --ergebnis eval/synthetic/results/ergebnis.csv --ground-truth eval/synthetic/ground_truth.csv
"""
from __future__ import annotations

import argparse
import csv


def load_csv(path: str, key: str) -> dict[str, dict]:
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        return {row[key].strip(): row for row in reader}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ergebnis", required=True)
    parser.add_argument("--ground-truth", required=True)
    args = parser.parse_args()

    actual = load_csv(args.ergebnis, "doc_id")
    expected = load_csv(args.ground_truth, "doc_id")

    missing = set(expected) - set(actual)
    if missing:
        print(f"WARNUNG: {len(missing)} Beleg(e) aus ground truth fehlen im Ergebnis: {sorted(missing)}")

    tp = tn = fp = fn = 0  # "positiv" = hinschauen
    mismatches = []

    for doc_id, exp_row in expected.items():
        if doc_id not in actual:
            continue
        exp = exp_row["erwartete_entscheidung"].strip()
        got = actual[doc_id]["entscheidung"].strip()
        if exp == "hinschauen" and got == "hinschauen":
            tp += 1
        elif exp == "freigeben" and got == "freigeben":
            tn += 1
        elif exp == "freigeben" and got == "hinschauen":
            fp += 1
            mismatches.append((doc_id, exp, got, "false hinschauen - unnötige manuelle Prüfung, aber sicher"))
        elif exp == "hinschauen" and got == "freigeben":
            fn += 1
            mismatches.append((doc_id, exp, got, "** false freigeben - GEFÄHRLICH, Fehler hätte Geld gekostet **"))

    n = tp + tn + fp + fn
    accuracy = (tp + tn) / n if n else 0.0

    print(f"Belege verglichen: {n}")
    print(f"Richtig freigeben (TN): {tn}")
    print(f"Richtig hinschauen (TP): {tp}")
    print(f"Falsch hinschauen (FP, unnötig aber sicher): {fp}")
    print(f"Falsch freigeben (FN, GEFÄHRLICH): {fn}")
    print(f"Accuracy: {accuracy:.1%}")
    print()
    if fn == 0:
        print("OK: Keine gefährlichen Fehlentscheidungen (false freigeben = 0).")
    else:
        print(f"FEHLER: {fn} gefährliche Fehlentscheidung(en) - siehe unten.")

    if mismatches:
        print("\nAbweichungen:")
        for doc_id, exp, got, note in mismatches:
            print(f"  - {doc_id}: erwartet={exp}, erhalten={got} ({note})")


if __name__ == "__main__":
    main()
