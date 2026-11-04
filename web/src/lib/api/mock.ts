/**
 * Demo adapter. Serves the real results of the last full Python run over the 16
 * sample receipts (results/ergebnis.csv + results/extracted/*.json).
 *
 * The check engine stays in Python. The ONLY thing simulated here is how the three
 * policy-tunable findings (D1, D6, F1) react to a changed policy in the browser,
 * so the "change tolerance → preview" workflow can be demonstrated without a
 * backend. In live mode the Python pipeline recomputes everything.
 */
import sample from "@/lib/mock/sample-results.json";
import type {
  BelegApi,
  BelegResult,
  CheckFinding,
  Decision,
  ManualDecision,
  PolicyOverrides,
  RunResult,
} from "./types";

const assets = import.meta.glob<{ url: string }>("/src/assets/belege/*.asset.json", {
  eager: true,
  import: "default",
});

function assetUrl(fileName: string): string | null {
  const hit = Object.entries(assets).find(([path]) => path.endsWith(`/${fileName}.asset.json`));
  return hit ? hit[1].url : null;
}

export const DEFAULT_POLICY: PolicyOverrides = {
  extra_items_tolerance_pct: 10,
  mandatory_review_amount_eur: 50000,
  no_po_match_means_hinschauen: true,
  line_arithmetic_tolerance_per_unit_eur: 0.005,
};

const OVERRIDES_KEY = "beleg.overrides.v1";

type RawSample = Omit<BelegResult, "manual" | "previewUrl" | "originalUrl">;

function loadOverrides(): Record<string, ManualDecision> {
  if (typeof window === "undefined") return {};
  try {
    return JSON.parse(window.localStorage.getItem(OVERRIDES_KEY) ?? "{}");
  } catch {
    return {};
  }
}

function saveOverrides(data: Record<string, ManualDecision>) {
  window.localStorage.setItem(OVERRIDES_KEY, JSON.stringify(data));
}

const fmt = (n: number) => n.toFixed(2);

/** Re-evaluates only the policy-tunable findings D1, D6, F1. */
export function applyPolicy(doc: RawSample, policy: PolicyOverrides): RawSample {
  const tunable = new Set(["D1", "D6", "F1"]);
  const all = [...doc.blockingReasons, ...doc.infoNotes];
  const blocking: CheckFinding[] = doc.blockingReasons.filter((f) => !tunable.has(f.id));
  const info: CheckFinding[] = doc.infoNotes.filter((f) => !tunable.has(f.id));

  // D1 — order reference present
  const d1 = all.find((f) => f.id === "D1");
  if (d1) {
    if (doc.orderReference) info.push(d1);
    else (policy.no_po_match_means_hinschauen ? blocking : info).push(d1);
  }

  // D6 — extra, not-ordered items vs. tolerance
  const d6 = all.find((f) => f.id === "D6");
  if (d6) {
    const pct = /\(([\d.]+)% des Bestellwerts/.exec(d6.message);
    if (pct) {
      const value = parseFloat(pct[1]);
      const base = d6.message.replace(/ (Über|Innerhalb) der Toleranz von [\d.]+%\.$/, "");
      const over = value > policy.extra_items_tolerance_pct;
      const msg = `${base} ${over ? "Über" : "Innerhalb"} der Toleranz von ${policy.extra_items_tolerance_pct}%.`;
      (over ? blocking : info).push({ id: "D6", message: msg });
    } else {
      (doc.blockingReasons.includes(d6) ? blocking : info).push(d6);
    }
  }

  // F1 — mandatory review amount
  if (all.some((f) => f.id === "F1") && doc.grossAmount != null) {
    const t = policy.mandatory_review_amount_eur;
    if (doc.grossAmount > t) {
      blocking.push({
        id: "F1",
        message: `Rechnungsbetrag ${fmt(doc.grossAmount)} € überschreitet die Freigabegrenze von ${fmt(t)} € - Vier-Augen-Prinzip greift immer.`,
      });
    } else {
      info.push({ id: "F1", message: `Rechnungsbetrag ${fmt(doc.grossAmount)} € unterhalb der Freigabegrenze von ${fmt(t)} €.` });
    }
  }

  const order = (a: CheckFinding, b: CheckFinding) => a.id.localeCompare(b.id, "de", { numeric: true });
  blocking.sort(order);
  info.sort(order);
  return {
    ...doc,
    blockingReasons: blocking,
    infoNotes: info,
    autoDecision: blocking.length ? "hinschauen" : "freigeben",
  };
}

function build(policy: PolicyOverrides, committed: boolean): RunResult {
  const overrides = loadOverrides();
  const docs: BelegResult[] = (sample as RawSample[]).map((raw) => {
    const doc = applyPolicy(raw, policy);
    const isImage = /\.(jpe?g|png|webp)$/i.test(doc.fileName);
    return {
      ...doc,
      manual: overrides[doc.docId] ?? null,
      previewUrl: isImage ? assetUrl(doc.fileName) : assetUrl(`${doc.docId}.png`),
      originalUrl: assetUrl(doc.fileName),
    };
  });
  const free = docs.filter((d) => (d.manual?.entscheidung ?? d.autoDecision) === "freigeben").length;
  return {
    docs,
    summary: { freigeben: free, hinschauen: docs.length - free, gesamt: docs.length },
    committed,
    policyUsed: policy,
  };
}

const wait = (ms: number) => new Promise((r) => setTimeout(r, ms));

export const mockApi: BelegApi = {
  mode: "demo",
  async defaultPolicy() {
    return DEFAULT_POLICY;
  },
  async analyze({ policy }) {
    await wait(450);
    return build(policy, false);
  },
  async commit({ policy }) {
    await wait(700);
    return build(policy, true);
  },
  async override({ docId, decision, note, originalDecision }) {
    const data = loadOverrides();
    const record: ManualDecision = {
      entscheidung: decision as Decision,
      notiz: note,
      automatischWar: originalDecision,
      zeitpunkt: new Date().toISOString(),
    };
    data[docId] = record;
    saveOverrides(data);
    return record;
  },
  async upload(files) {
    await wait(300);
    return { folder: "demo-upload", files: files.map((f) => f.name) };
  },
};
