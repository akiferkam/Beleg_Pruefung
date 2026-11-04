/**
 * Frontend contract for the Python backend (api/app.py + scripts/pipeline.py).
 * Field names are camelCase here; the REST adapter maps them from the Flask JSON
 * (doc_id, entscheidung, gruende, info_notes, manuell, ...).
 */

export type Decision = "freigeben" | "hinschauen";

export interface CheckFinding {
  /** Check code from the catalog A1–F2, e.g. "D6". */
  id: string;
  message: string;
}

export interface LineItem {
  description: string | null;
  quantity: number | null;
  unitPrice: number | null;
  lineTotal: number | null;
}

export interface ManualDecision {
  entscheidung: Decision;
  notiz: string;
  automatischWar: Decision;
  zeitpunkt: string;
}

export interface BelegResult {
  docId: string;
  fileName: string;
  /** Automatic decision by the deterministic check engine. */
  autoDecision: Decision;
  /** Manual override if a person decided after viewing the original. */
  manual: ManualDecision | null;
  documentType: string | null;
  supplier: string | null;
  supplierAddress: string | null;
  supplierTaxId: string | null;
  iban: string | null;
  invoiceNumber: string | null;
  invoiceDate: string | null;
  orderReference: string | null;
  currency: string;
  netAmount: number | null;
  vatRatePct: number | null;
  vatAmount: number | null;
  grossAmount: number | null;
  skonto: string | null;
  manipulationAttempt: string | null;
  lineItems: LineItem[];
  blockingReasons: CheckFinding[];
  infoNotes: CheckFinding[];
  previewUrl: string | null;
  originalUrl: string | null;
  isNewUpload?: boolean;
  extractionError?: string | null;
}

/** The three policy values that are editable in the original web UI. */
export interface PolicyOverrides {
  extra_items_tolerance_pct: number;
  mandatory_review_amount_eur: number;
  no_po_match_means_hinschauen: boolean;
  line_arithmetic_tolerance_per_unit_eur: number;
}

export interface RunResult {
  docs: BelegResult[];
  summary: { freigeben: number; hinschauen: number; gesamt: number };
  committed: boolean;
  policyUsed: PolicyOverrides;
}

export interface UploadResult {
  folder: string;
  files: string[];
}

export interface BelegApi {
  readonly mode: "demo" | "live";
  defaultPolicy(): Promise<PolicyOverrides>;
  /** Preview run — never writes the ledger. Maps to POST /api/analyze. */
  analyze(input: { folder?: string; policy: PolicyOverrides }): Promise<RunResult>;
  /** Real run — writes ledger + ergebnis.csv/.md. Maps to POST /api/commit. */
  commit(input: { folder?: string; policy: PolicyOverrides }): Promise<RunResult>;
  /** Manual decision after viewing the original. Maps to POST /api/override. */
  override(input: { docId: string; decision: Decision; note: string; originalDecision: Decision }): Promise<ManualDecision>;
  /** Maps to POST /api/upload (multipart). */
  upload(files: File[]): Promise<UploadResult>;
}

export function finalDecision(doc: BelegResult): Decision {
  return doc.manual?.entscheidung ?? doc.autoDecision;
}
