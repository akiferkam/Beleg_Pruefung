import { createFileRoute, Link } from "@tanstack/react-router";
import { ExternalLink } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/beleg/page-header";
import { StatusBadge, SourceBadge, displayStatus } from "@/components/beleg/status";
import { eur, useBeleg } from "@/lib/beleg-store";

export const Route = createFileRoute("/freigegeben")({
  head: () => ({ meta: [{ title: "Freigegeben – Beleg-Prüfung" }] }),
  component: Freigegeben,
});

function Freigegeben() {
  const { docs } = useBeleg();
  const resolved = docs.filter((d) => displayStatus(d) !== "zu-pruefen");

  return (
    <div className="space-y-6 animate-rise">
      <PageHeader title="Freigegeben" description="Alle entschiedenen Belege - automatisch oder nach manueller Prüfung." />

      {resolved.length === 0 ? (
        <Card className="shadow-card">
          <CardContent className="py-14 text-center text-sm text-muted-foreground">Noch keine entschiedenen Belege.</CardContent>
        </Card>
      ) : (
        <Card className="shadow-card">
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Beleg</TableHead>
                  <TableHead>Lieferant</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Quelle</TableHead>
                  <TableHead className="text-right">Betrag</TableHead>
                  <TableHead />
                </TableRow>
              </TableHeader>
              <TableBody>
                {resolved.map((doc) => (
                  <TableRow key={doc.docId}>
                    <TableCell>
                      <Link to="/belege/$docId" params={{ docId: doc.docId }} className="font-medium hover:underline">
                        {doc.docId}
                      </Link>
                    </TableCell>
                    <TableCell className="text-muted-foreground">{doc.supplier ?? "–"}</TableCell>
                    <TableCell>
                      <StatusBadge doc={doc} />
                    </TableCell>
                    <TableCell>
                      <SourceBadge doc={doc} />
                    </TableCell>
                    <TableCell className="text-right tabular">{eur(doc.grossAmount)}</TableCell>
                    <TableCell>
                      {doc.originalUrl && (
                        <Button asChild variant="ghost" size="sm">
                          <a href={doc.originalUrl} target="_blank" rel="noreferrer">
                            <ExternalLink className="h-3.5 w-3.5" />
                          </a>
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
