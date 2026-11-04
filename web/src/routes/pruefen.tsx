import { createFileRoute, Link } from "@tanstack/react-router";
import { ExternalLink } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { PageHeader } from "@/components/beleg/page-header";
import { RunBar } from "@/components/beleg/run-bar";
import { DocThumb } from "@/components/beleg/doc-thumb";
import { DecisionPanel } from "@/components/beleg/decision-panel";
import { CheckCode, displayStatus } from "@/components/beleg/status";
import { eur, useBeleg } from "@/lib/beleg-store";

export const Route = createFileRoute("/pruefen")({
  head: () => ({
    meta: [
      { title: "Zu prüfen – Beleg-Prüfung" },
      { name: "description", content: "Warteschlange der Belege, die eine manuelle Entscheidung brauchen." },
    ],
  }),
  component: Pruefen,
});

function Pruefen() {
  const { docs, loading } = useBeleg();
  const queue = docs.filter((d) => displayStatus(d) === "zu-pruefen");

  return (
    <div className="space-y-6 animate-rise">
      <PageHeader
        title="Zu prüfen"
        description="Jede Karte kann geöffnet, nachvollzogen und in Sekunden entschieden werden. Entschiedene Belege verschwinden sofort aus dieser Liste."
      />
      <RunBar />

      {!loading && queue.length === 0 && (
        <Card className="shadow-card">
          <CardContent className="flex flex-col items-center gap-2 py-14 text-center">
            <p className="text-base font-medium">Keine offenen Punkte</p>
            <p className="text-sm text-muted-foreground">Alle Belege sind automatisch oder manuell entschieden.</p>
          </CardContent>
        </Card>
      )}

      <div className="space-y-4">
        {queue.map((doc) => (
          <Card key={doc.docId} className="shadow-card">
            <CardContent className="flex flex-col gap-4 p-5 sm:flex-row">
              <DocThumb src={doc.previewUrl} alt={doc.docId} className="h-28 w-24 shrink-0 sm:h-32 sm:w-28" />
              <div className="min-w-0 flex-1 space-y-3">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div className="min-w-0">
                    <Link to="/belege/$docId" params={{ docId: doc.docId }} className="font-semibold hover:underline">
                      {doc.docId}
                    </Link>
                    <p className="truncate text-sm text-muted-foreground">
                      {doc.supplier ?? "Lieferant unbekannt"}
                      {doc.orderReference && ` · Bestellnr. ${doc.orderReference}`}
                    </p>
                  </div>
                  <p className="shrink-0 text-base font-semibold tabular">{eur(doc.grossAmount)}</p>
                </div>

                {doc.fehler && <p className="text-sm text-danger">Fehler: {doc.fehler}</p>}

                <ul className="space-y-1.5">
                  {doc.blockingReasons.map((r) => (
                    <li key={r.id} className="flex items-start gap-2 text-sm text-danger">
                      <CheckCode id={r.id} />
                      <span>{r.message}</span>
                    </li>
                  ))}
                </ul>

                <Collapsible>
                  <CollapsibleTrigger asChild>
                    <button className="text-xs text-muted-foreground underline underline-offset-2">
                      Alle geprüften Punkte ({doc.infoNotes.length}) anzeigen
                    </button>
                  </CollapsibleTrigger>
                  <CollapsibleContent className="mt-2 max-h-48 space-y-1 overflow-y-auto rounded-md bg-muted/50 p-3">
                    {doc.infoNotes.map((r, i) => (
                      <p key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
                        <CheckCode id={r.id} />
                        <span>{r.message}</span>
                      </p>
                    ))}
                  </CollapsibleContent>
                </Collapsible>

                <div className="flex flex-wrap items-center gap-2 pt-1">
                  {doc.originalUrl && (
                    <Button asChild variant="outline" size="sm">
                      <a href={doc.originalUrl} target="_blank" rel="noreferrer">
                        Beleg öffnen <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    </Button>
                  )}
                </div>

                <DecisionPanel doc={doc} compact />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
