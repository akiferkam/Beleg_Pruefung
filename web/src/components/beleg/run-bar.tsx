import { Database, Eye, Loader2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { dateTimeDe, useBeleg } from "@/lib/beleg-store";

/**
 * Keeps the original distinction visible: "Analysieren" is a preview that never
 * writes, "In Ledger übernehmen" is the real, ledger-writing run.
 */
export function RunBar() {
  const { analyze, commit, loading, uncommitted, lastCommitAt, run } = useBeleg();
  return (
    <div className="flex flex-col gap-3 rounded-xl border bg-card p-4 shadow-card sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 flex h-9 w-9 items-center justify-center rounded-lg bg-accent text-accent-foreground">
          {uncommitted ? <Eye className="h-4 w-4" /> : <Database className="h-4 w-4" />}
        </div>
        <div>
          <p className="text-sm font-medium">
            {uncommitted ? "Vorschau – noch nicht im Ledger" : "Stand entspricht dem Ledger"}
          </p>
          <p className="text-xs text-muted-foreground">
            {uncommitted
              ? "Analysieren ist beliebig wiederholbar und verändert nichts."
              : "Letzte Übernahme gerade eben."}
            {lastCommitAt && ` Letzte Übernahme: ${dateTimeDe(lastCommitAt)}.`}
          </p>
        </div>
      </div>
      <div className="flex gap-2">
        <Button variant="outline" onClick={() => analyze()} disabled={loading}>
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
          Analysieren
        </Button>
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button disabled={loading || !run}>
              <Database className="h-4 w-4" />
              In Ledger übernehmen
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Ergebnis ins Ledger übernehmen?</AlertDialogTitle>
              <AlertDialogDescription>
                Das schreibt {run?.summary.gesamt ?? 0} Belege dauerhaft ins Ledger und aktualisiert ergebnis.csv/.md.
                Spätere Läufe erkennen diese Belege dann als bereits verarbeitet (Duplikats- und Mengenprüfung).
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Abbrechen</AlertDialogCancel>
              <AlertDialogAction onClick={() => commit()}>Übernehmen</AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  );
}
