import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { ArrowLeft, ExternalLink } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { DocThumb } from "@/components/beleg/doc-thumb";
import { DecisionPanel } from "@/components/beleg/decision-panel";
import { StatusBadge, SourceBadge, CheckCode } from "@/components/beleg/status";
import { dateDe, eur, useBeleg } from "@/lib/beleg-store";

export const Route = createFileRoute("/belege/$docId")({
  head: ({ params }) => ({
    meta: [{ title: `${params.docId} – Beleg-Prüfung` }],
  }),
  component: BelegDetail,
});

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-sm font-medium">{value ?? "–"}</p>
    </div>
  );
}

function BelegDetail() {
  const { docId } = Route.useParams();
  const { getDoc, loading } = useBeleg();
  const doc = getDoc(docId);

  if (!doc) {
    if (loading) return <p className="text-sm text-muted-foreground">Lädt …</p>;
    throw notFound();
  }

  return (
    <div className="space-y-6 animate-rise">
      <div>
        <Button asChild variant="ghost" size="sm" className="mb-2 -ml-2">
          <Link to="/pruefen">
            <ArrowLeft className="h-4 w-4" /> Zurück zur Warteschlange
          </Link>
        </Button>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-semibold tracking-tight">{doc.docId}</h1>
          <StatusBadge doc={doc} />
          <SourceBadge doc={doc} />
        </div>
        <p className="mt-1 text-sm text-muted-foreground">{doc.documentType ?? "Belegtyp unbekannt"} · {doc.fileName}</p>
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        <Card className="shadow-card lg:col-span-2">
          <CardContent className="p-4">
            <DocThumb src={doc.previewUrl} alt={doc.docId} className="aspect-[3/4] w-full" />
            {doc.originalUrl && (
              <Button asChild variant="outline" className="mt-3 w-full">
                <a href={doc.originalUrl} target="_blank" rel="noreferrer">
                  Original öffnen (PDF/Bild) <ExternalLink className="h-4 w-4" />
                </a>
              </Button>
            )}
          </CardContent>
        </Card>

        <Card className="shadow-card lg:col-span-3">
          <CardHeader>
            <CardTitle className="text-base">Belegdaten</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <Field label="Lieferant" value={doc.supplier} />
            <Field label="Adresse" value={doc.supplierAddress} />
            <Field label="Steuernr. / USt-IdNr" value={doc.supplierTaxId} />
            <Field label="IBAN" value={doc.iban} />
            <Field label="Rechnungsnr." value={doc.invoiceNumber} />
            <Field label="Rechnungsdatum" value={dateDe(doc.invoiceDate)} />
            <Field label="Bestellnummer" value={doc.orderReference} />
            <Field label="Nettobetrag" value={eur(doc.netAmount)} />
            <Field label="USt-Satz" value={doc.vatRatePct != null ? `${doc.vatRatePct} %` : null} />
            <Field label="USt-Betrag" value={eur(doc.vatAmount)} />
            <Field label="Bruttobetrag" value={eur(doc.grossAmount)} />
            <Field label="Skonto" value={doc.skonto} />
          </CardContent>
        </Card>
      </div>

      {doc.manipulationAttempt && (
        <Card className="border-danger/40 bg-danger-soft shadow-card">
          <CardContent className="p-4 text-sm text-danger">
            <strong>An ein Prüfsystem gerichtete Formulierung gefunden und ignoriert:</strong> „{doc.manipulationAttempt}“
          </CardContent>
        </Card>
      )}

      {doc.lineItems.length > 0 && (
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle className="text-base">Positionen</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead className="text-right">Menge</TableHead>
                  <TableHead className="text-right">Einzelpreis</TableHead>
                  <TableHead className="text-right">Gesamt</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {doc.lineItems.map((item, i) => (
                  <TableRow key={i}>
                    <TableCell>{item.description ?? "–"}</TableCell>
                    <TableCell className="text-right tabular">{item.quantity ?? "–"}</TableCell>
                    <TableCell className="text-right tabular">{item.unitPrice != null ? eur(item.unitPrice) : "–"}</TableCell>
                    <TableCell className="text-right tabular">{item.lineTotal != null ? eur(item.lineTotal) : "–"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      <Card className="shadow-card">
        <CardHeader>
          <CardTitle className="text-base">Geprüfte Punkte</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {doc.blockingReasons.length > 0 && (
            <div className="space-y-1.5">
              {doc.blockingReasons.map((r) => (
                <p key={r.id} className="flex items-start gap-2 text-sm text-danger">
                  <CheckCode id={r.id} /> <span>{r.message}</span>
                </p>
              ))}
            </div>
          )}
          <div className="space-y-1">
            {doc.infoNotes.map((r, i) => (
              <p key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
                <CheckCode id={r.id} /> <span>{r.message}</span>
              </p>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="shadow-card">
        <CardHeader>
          <CardTitle className="text-base">Entscheidung</CardTitle>
        </CardHeader>
        <CardContent>
          {doc.manual && (
            <p className="mb-3 rounded-md bg-warning-soft p-3 text-sm text-warning">
              Manuell <strong>{doc.manual.entscheidung}</strong> (automatisch war: {doc.manual.automatischWar}).
              {doc.manual.notiz && ` Notiz: ${doc.manual.notiz}`}
            </p>
          )}
          <DecisionPanel doc={doc} />
        </CardContent>
      </Card>
    </div>
  );
}
