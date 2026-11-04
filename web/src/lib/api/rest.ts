/**
 * Live adapter for the Flask API (api/app.py). Endpoints are used as-is:
 *   POST /api/analyze   POST /api/commit   POST /api/override   POST /api/upload
 *   GET  /doc?path=...  GET  /thumb?path=...
 * The Python side is unchanged; this file only maps its JSON to the UI types.
 * Note: the Flask app must allow CORS from the frontend origin (or be proxied).
 */
import type { BelegApi, BelegResult, CheckFinding, Decision, ManualDecision, PolicyOverrides, RunResult } from "./types";
import { DEFAULT_POLICY } from "./mock";

type FlaskFinding = { id: string; nachricht: string };
type FlaskManual = { entscheidung: Decision; notiz: string; automatisch_war: Decision; zeitpunkt: string } | null;
interface FlaskLineItem {
  beschreibung: string | null;
  menge: number | null;
  einzelpreis: number | null;
  gesamt: number | null;
}
interface FlaskDoc {
  doc_id: string;
  datei: string;
  pfad: string;
  neu_hochgeladen: boolean;
  entscheidung: Decision;
  manuell: FlaskManual;
  lieferant: string | null;
  rechnungsnr: string | null;
  betrag_brutto_eur: number | null;
  bestellnummer: string | null;
  gruende: FlaskFinding[];
  info_notes: FlaskFinding[];
  fehler: string | null;
  belegtyp: string | null;
  lieferant_adresse: string | null;
  lieferant_steuernr: string | null;
  iban: string | null;
  rechnungsdatum: string | null;
  betrag_netto_eur: number | null;
  ust_satz_pct: number | null;
  ust_betrag_eur: number | null;
  skonto: string | null;
  manipulationsversuch: string | null;
  positionen: FlaskLineItem[];
}

const mapFindings = (list: FlaskFinding[]): CheckFinding[] => list.map((f) => ({ id: f.id, message: f.nachricht }));
const mapManual = (m: FlaskManual): ManualDecision | null =>
  m ? { entscheidung: m.entscheidung, notiz: m.notiz, automatischWar: m.automatisch_war, zeitpunkt: m.zeitpunkt } : null;

export function createRestApi(baseUrl: string): BelegApi {
  const url = (p: string) => `${baseUrl.replace(/\/$/, "")}${p}`;

  async function post<T>(path: string, body: unknown): Promise<T> {
    const res = await fetch(url(path), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const json = await res.json();
    if (!res.ok) throw new Error(json.error ?? `Fehler ${res.status}`);
    return json as T;
  }

  function mapDoc(d: FlaskDoc): BelegResult {
    const q = encodeURIComponent(d.pfad);
    return {
      docId: d.doc_id,
      fileName: d.datei,
      autoDecision: d.entscheidung,
      manual: mapManual(d.manuell),
      documentType: d.belegtyp,
      supplier: d.lieferant,
      supplierAddress: d.lieferant_adresse,
      supplierTaxId: d.lieferant_steuernr,
      iban: d.iban,
      invoiceNumber: d.rechnungsnr,
      invoiceDate: d.rechnungsdatum,
      orderReference: d.bestellnummer,
      currency: "EUR",
      netAmount: d.betrag_netto_eur,
      vatRatePct: d.ust_satz_pct,
      vatAmount: d.ust_betrag_eur,
      grossAmount: d.betrag_brutto_eur,
      skonto: d.skonto,
      manipulationAttempt: d.manipulationsversuch,
      lineItems: (d.positionen ?? []).map((p) => ({
        description: p.beschreibung,
        quantity: p.menge,
        unitPrice: p.einzelpreis,
        lineTotal: p.gesamt,
      })),
      blockingReasons: mapFindings(d.gruende),
      infoNotes: mapFindings(d.info_notes),
      previewUrl: url(`/thumb?path=${q}`),
      originalUrl: url(`/doc?path=${q}`),
      isNewUpload: d.neu_hochgeladen,
      extractionError: d.fehler,
    };
  }

  async function run(path: string, input: { folder?: string; policy: PolicyOverrides }): Promise<RunResult> {
    const r = await post<{ docs: FlaskDoc[]; summary: RunResult["summary"]; committed: boolean; policy_used: PolicyOverrides }>(
      path,
      { folder: input.folder, policy: input.policy },
    );
    return { docs: r.docs.map(mapDoc), summary: r.summary, committed: r.committed, policyUsed: r.policy_used };
  }

  return {
    mode: "live",
    async defaultPolicy() {
      return DEFAULT_POLICY;
    },
    analyze: (i) => run("/api/analyze", i),
    commit: (i) => run("/api/commit", i),
    async override({ docId, decision, note, originalDecision }) {
      const r = await post<{ manuell: FlaskManual }>("/api/override", {
        doc_id: docId,
        decision,
        note,
        original_decision: originalDecision,
      });
      return mapManual(r.manuell)!;
    },
    async upload(files) {
      const form = new FormData();
      files.forEach((f) => form.append("files", f));
      const res = await fetch(url("/api/upload"), { method: "POST", body: form });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error ?? `Fehler ${res.status}`);
      return { folder: json.folder, files: json.dateien };
    },
  };
}
