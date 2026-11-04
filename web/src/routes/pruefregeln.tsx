import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/beleg/page-header";
import { useBeleg } from "@/lib/beleg-store";

export const Route = createFileRoute("/pruefregeln")({
  head: () => ({ meta: [{ title: "Prüfregeln – Beleg-Prüfung" }] }),
  component: Pruefregeln,
});

function Pruefregeln() {
  const { policy, setPolicy, loading } = useBeleg();
  const [draft, setDraft] = useState(policy);

  const dirty = JSON.stringify(draft) !== JSON.stringify(policy);

  return (
    <div className="max-w-2xl space-y-6 animate-rise">
      <PageHeader
        title="Prüfregeln"
        description="Schwellenwerte live ändern und sofort gegen den letzten Lauf neu auswerten - ohne neuen Vision-Aufruf."
      />

      <Card className="shadow-card">
        <CardHeader>
          <CardTitle className="text-base">Toleranzen & Pflichten</CardTitle>
          <CardDescription>Entspricht den Policy-Feldern in config.yaml.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="space-y-1.5">
            <Label htmlFor="tol">Toleranz nicht bestellte Zusatzpositionen (%)</Label>
            <Input
              id="tol"
              type="number"
              step="0.1"
              value={draft.extra_items_tolerance_pct}
              onChange={(e) => setDraft({ ...draft, extra_items_tolerance_pct: parseFloat(e.target.value) || 0 })}
            />
            <p className="text-xs text-muted-foreground">
              Zusatzpositionen bis zu diesem Anteil des Bestellwerts lösen kein hinschauen aus.
            </p>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="limit">Freigabegrenze / Vier-Augen-Pflicht (EUR brutto)</Label>
            <Input
              id="limit"
              type="number"
              step="100"
              value={draft.mandatory_review_amount_eur}
              onChange={(e) => setDraft({ ...draft, mandatory_review_amount_eur: parseFloat(e.target.value) || 0 })}
            />
            <p className="text-xs text-muted-foreground">Oberhalb dieser Grenze immer hinschauen, unabhängig von sonstigen Prüfungen.</p>
          </div>

          <div className="flex items-center justify-between rounded-lg border p-3">
            <div>
              <Label htmlFor="po">Beleg ohne Bestellbezug → immer hinschauen</Label>
              <p className="text-xs text-muted-foreground">Ohne Bestellung nicht prüfbar, ob die Leistung je bestellt wurde.</p>
            </div>
            <Switch
              id="po"
              checked={draft.no_po_match_means_hinschauen}
              onCheckedChange={(v) => setDraft({ ...draft, no_po_match_means_hinschauen: v })}
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="arith">Arithmetik-Toleranz pro Einheit (EUR)</Label>
            <Input
              id="arith"
              type="number"
              step="0.001"
              value={draft.line_arithmetic_tolerance_per_unit_eur}
              onChange={(e) => setDraft({ ...draft, line_arithmetic_tolerance_per_unit_eur: parseFloat(e.target.value) || 0 })}
            />
            <p className="text-xs text-muted-foreground">Für gerundete Anzeige-Einzelpreise (z.B. 0,021 € wird als 0,02 € angezeigt).</p>
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setDraft(policy)} disabled={!dirty}>
              Verwerfen
            </Button>
            <Button onClick={() => setPolicy(draft)} disabled={!dirty || loading}>
              Übernehmen &amp; neu auswerten
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
