"""Kontrollkatalog A-F: orchestriert alle Einzel-Checks zu einer Finding-Liste.

Reihenfolge ist Absicht (siehe README): zuerst Lesbarkeit (A1/A2), dann
Belegtyp (A3) - erst danach sind inhaltliche Prüfungen (B-F) überhaupt
sinnvoll. Ein Lieferschein ohne Beträge auf USt-Arithmetik zu prüfen, wäre
Unsinn und nur Rauschen im Bericht.
"""
from __future__ import annotations

from . import arithmetic, business, doctype, formal, fraud, orders, readability
from .base import Finding


def run_all_checks(*, intake_result, extraction, extraction_error, grounding_report,
                    orders_db, ledger, config, file_hash) -> tuple[list[Finding], dict]:
    findings: list[Finding] = []
    extra_context: dict = {"po": None, "matched_items": [], "extra_items": []}

    f_a1 = readability.check_file_readable(intake_result)
    findings.append(f_a1)
    if not f_a1.passed:
        return findings, extra_context

    f_a2 = readability.check_fields_readable(extraction, extraction_error)
    findings.append(f_a2)
    if not f_a2.passed:
        return findings, extra_context

    findings.append(doctype.check_is_invoice(extraction))
    findings.append(readability.check_pages_complete(intake_result, extraction))
    findings.append(readability.check_grounding(grounding_report))

    if not findings[2].passed:  # A3 (document_type != Rechnung)
        return findings, extra_context

    policy = config["policy"]

    # B: formal
    findings.append(formal.check_recipient(extraction, config["company"]))
    findings.append(formal.check_supplier_present(extraction))
    findings.append(formal.check_supplier_tax_id(extraction))
    findings.append(formal.check_invoice_number_and_date(extraction))
    findings.append(formal.check_amounts_disclosed(extraction))
    findings.append(formal.check_reverse_charge_formalities(extraction, config["company"]["vat_id"]))
    findings.append(formal.check_leistungsdatum(extraction))

    # C: Arithmetik
    findings.append(arithmetic.check_line_arithmetic(extraction, policy["line_arithmetic_tolerance_per_unit_eur"]))
    findings.append(arithmetic.check_net_sum(extraction, policy["net_sum_tolerance_eur"]))
    findings.append(arithmetic.check_vat_rate_valid(extraction, policy["valid_vat_rates_pct"]))
    findings.append(arithmetic.check_vat_amount(extraction, policy["vat_amount_tolerance_eur"]))
    findings.append(arithmetic.check_gross_amount(extraction, policy["gross_amount_tolerance_eur"]))
    findings.append(arithmetic.check_currency_and_positive(extraction))

    # D: Bestellabgleich
    findings.append(orders.check_order_reference_present(extraction, policy["no_po_match_means_hinschauen"]))
    f_d2, po = orders.check_order_exists(extraction, orders_db)
    findings.append(f_d2)
    extra_context["po"] = po

    if po is not None:
        matched_items, extra_items = orders.split_matched_items(extraction.get("line_items") or [], po.artikel)
        extra_context["matched_items"] = matched_items
        extra_context["extra_items"] = extra_items
        findings.append(orders.check_supplier_matches_order(extraction, po, policy["supplier_fuzzy_match_min_score"]))
        findings.append(orders.check_unit_price(extraction, po, matched_items, policy["line_arithmetic_tolerance_per_unit_eur"]))
        findings.append(orders.check_cumulative_quantity(extraction, po, matched_items, ledger))
        findings.append(orders.check_extra_items(extraction, po, extra_items, policy["extra_items_tolerance_pct"]))
        findings.append(orders.check_rahmenvertrag_info(po))

    # E: Betrug/Duplikate
    findings.append(fraud.check_file_hash_duplicate(file_hash, ledger))
    findings.append(fraud.check_invoice_number_duplicate(extraction, ledger))
    import ledger as ledger_mod
    fp = ledger_mod.line_items_fingerprint(extraction.get("line_items") or [])
    extra_context["fingerprint"] = fp
    findings.append(fraud.check_content_duplicate(extraction, fp, ledger))
    findings.append(fraud.check_iban_checksum(extraction))
    findings.append(fraud.check_iban_matches_history(extraction, ledger))
    findings.append(fraud.check_manipulation_attempt(extraction))

    # F: Geschäftsregeln
    findings.append(business.check_amount_threshold(extraction, policy["mandatory_review_amount_eur"]))
    findings.append(business.check_skonto(extraction))

    return findings, extra_context
