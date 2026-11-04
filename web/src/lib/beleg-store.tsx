import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { toast } from "sonner";
import { api, finalDecision, type BelegResult, type Decision, type PolicyOverrides, type RunResult } from "@/lib/api";
import { DEFAULT_POLICY } from "@/lib/api/mock";

export type ActivityKind = "analyse" | "commit" | "manuell" | "upload" | "policy";
export interface Activity {
  id: string;
  kind: ActivityKind;
  at: string;
  title: string;
  detail?: string;
  docId?: string;
}

interface Store {
  mode: "demo" | "live";
  run: RunResult | null;
  docs: BelegResult[];
  loading: boolean;
  policy: PolicyOverrides;
  /** Ordner, der gerade analysiert wird (live-Modus). null = Standardordner (belege/) im Backend. */
  folder: string | null;
  /** Whether the current preview differs from the last ledger commit. */
  uncommitted: boolean;
  lastCommitAt: string | null;
  activity: Activity[];
  analyze: (policy?: PolicyOverrides, folderOverride?: string) => Promise<void>;
  commit: () => Promise<void>;
  decide: (doc: BelegResult, decision: Decision, note: string) => Promise<void>;
  setPolicy: (p: PolicyOverrides) => void;
  upload: (files: File[]) => Promise<void>;
  getDoc: (docId: string) => BelegResult | undefined;
}

const Ctx = createContext<Store | null>(null);
const POLICY_KEY = "beleg.policy.v1";
const FOLDER_KEY = "beleg.folder.v1";
const ACTIVITY_KEY = "beleg.activity.v1";
const COMMIT_KEY = "beleg.lastCommit.v1";

function readLocal<T>(key: string, fallback: T): T {
  try {
    const v = window.localStorage.getItem(key);
    return v ? (JSON.parse(v) as T) : fallback;
  } catch {
    return fallback;
  }
}

export function BelegProvider({ children }: { children: ReactNode }) {
  const [run, setRun] = useState<RunResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [policy, setPolicyState] = useState<PolicyOverrides>(DEFAULT_POLICY);
  const [folder, setFolder] = useState<string | null>(null);
  const [activity, setActivity] = useState<Activity[]>([]);
  const [lastCommitAt, setLastCommitAt] = useState<string | null>(null);
  const [uncommitted, setUncommitted] = useState(true);

  const log = useCallback((a: Omit<Activity, "id" | "at">) => {
    setActivity((prev) => {
      const next = [{ ...a, id: crypto.randomUUID(), at: new Date().toISOString() }, ...prev].slice(0, 60);
      window.localStorage.setItem(ACTIVITY_KEY, JSON.stringify(next));
      return next;
    });
  }, []);

  const analyze = useCallback(
    async (p?: PolicyOverrides, folderOverride?: string) => {
      const used = p ?? policy;
      const usedFolder = folderOverride ?? folder ?? undefined;
      setLoading(true);
      try {
        const r = await api.analyze({ policy: used, folder: usedFolder });
        setRun(r);
        setUncommitted(true);
        return void r;
      } catch (e) {
        toast.error("Analyse fehlgeschlagen", { description: (e as Error).message });
      } finally {
        setLoading(false);
      }
    },
    [policy, folder],
  );

  useEffect(() => {
    const p = readLocal(POLICY_KEY, DEFAULT_POLICY);
    setPolicyState(p);
    setFolder(readLocal<string | null>(FOLDER_KEY, null));
    setActivity(readLocal<Activity[]>(ACTIVITY_KEY, []));
    setLastCommitAt(readLocal<string | null>(COMMIT_KEY, null));
    void analyze(p);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const commit = useCallback(async () => {
    setLoading(true);
    try {
      const r = await api.commit({ policy, folder: folder ?? undefined });
      setRun(r);
      const at = new Date().toISOString();
      setLastCommitAt(at);
      window.localStorage.setItem(COMMIT_KEY, JSON.stringify(at));
      setUncommitted(false);
      log({
        kind: "commit",
        title: "In Ledger übernommen",
        detail: `${r.summary.freigeben} freigegeben · ${r.summary.hinschauen} hinschauen`,
      });
      toast.success("Ergebnis ins Ledger übernommen", { description: "ergebnis.csv und ergebnis.md wurden aktualisiert." });
    } catch (e) {
      toast.error("Übernahme fehlgeschlagen", { description: (e as Error).message });
    } finally {
      setLoading(false);
    }
  }, [policy, folder, log]);

  const decide = useCallback(
    async (doc: BelegResult, decision: Decision, note: string) => {
      try {
        const manual = await api.override({ docId: doc.docId, decision, note, originalDecision: doc.autoDecision });
        setRun((r) => (r ? { ...r, docs: r.docs.map((d) => (d.docId === doc.docId ? { ...d, manual } : d)) } : r));
        setUncommitted(true);
        log({
          kind: "manuell",
          docId: doc.docId,
          title: decision === "freigeben" ? "Manuell freigegeben" : "Hinschauen bestätigt",
          detail: `${doc.supplier ?? doc.docId}${note ? ` – „${note}“` : ""}`,
        });
        toast.success(decision === "freigeben" ? "Beleg freigegeben" : "Als geprüft markiert", {
          description: doc.supplier ?? doc.docId,
        });
      } catch (e) {
        toast.error("Entscheidung konnte nicht gespeichert werden", { description: (e as Error).message });
      }
    },
    [log],
  );

  const setPolicy = useCallback(
    (p: PolicyOverrides) => {
      setPolicyState(p);
      window.localStorage.setItem(POLICY_KEY, JSON.stringify(p));
      log({
        kind: "policy",
        title: "Prüfregeln geändert",
        detail: `Toleranz ${p.extra_items_tolerance_pct} % · Grenze ${p.mandatory_review_amount_eur.toLocaleString("de-DE")} € · Bestellbezug ${p.no_po_match_means_hinschauen ? "Pflicht" : "optional"}`,
      });
      void analyze(p);
    },
    [analyze, log],
  );

  const upload = useCallback(
    async (files: File[]) => {
      const r = await api.upload(files);
      log({ kind: "upload", title: `${r.files.length} Beleg(e) hochgeladen`, detail: r.files.slice(0, 3).join(", ") });
      // Im live-Modus liefert /api/upload einen neuen Ordner zurück - die folgenden
      // Analyse-/Commit-Aufrufe müssen genau diesen Ordner verwenden, sonst sieht
      // man die gerade hochgeladenen Belege nie in der Warteschlange.
      if (r.folder && r.folder !== "demo-upload") {
        setFolder(r.folder);
        window.localStorage.setItem(FOLDER_KEY, JSON.stringify(r.folder));
        await analyze(policy, r.folder);
      }
    },
    [log, analyze, policy],
  );

  const docs = run?.docs ?? [];
  const value = useMemo<Store>(
    () => ({
      mode: api.mode,
      run,
      docs,
      loading,
      policy,
      folder,
      uncommitted,
      lastCommitAt,
      activity,
      analyze,
      commit,
      decide,
      setPolicy,
      upload,
      getDoc: (id) => docs.find((d) => d.docId === id),
    }),
    [run, docs, loading, policy, folder, uncommitted, lastCommitAt, activity, analyze, commit, decide, setPolicy, upload],
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useBeleg() {
  const v = useContext(Ctx);
  if (!v) throw new Error("useBeleg must be used inside BelegProvider");
  return v;
}

export { finalDecision };

export const CHECK_GROUPS: Record<string, string> = {
  A: "Lesbarkeit & Format",
  B: "Formale Pflichtangaben (§14 UStG)",
  C: "Rechnerische Prüfung",
  D: "Bestellabgleich",
  E: "Betrug & Duplikate",
  F: "Geschäftsregeln",
};

export const eur = (n: number | null | undefined) =>
  n == null ? "–" : n.toLocaleString("de-DE", { style: "currency", currency: "EUR" });

export const dateDe = (iso: string | null | undefined) =>
  iso ? new Date(iso).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" }) : "–";

export const dateTimeDe = (iso: string) =>
  new Date(iso).toLocaleString("de-DE", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
