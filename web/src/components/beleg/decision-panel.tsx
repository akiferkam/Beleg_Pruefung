import { useState } from "react";
import { CheckCircle2, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import type { BelegResult } from "@/lib/api";
import { useBeleg } from "@/lib/beleg-store";

export function DecisionPanel({ doc, compact }: { doc: BelegResult; compact?: boolean }) {
  const { decide } = useBeleg();
  const [note, setNote] = useState(doc.manual?.notiz ?? "");
  const [busy, setBusy] = useState(false);
  const act = async (d: "freigeben" | "hinschauen") => {
    setBusy(true);
    await decide(doc, d, note.trim());
    setBusy(false);
  };
  return (
    <div className="space-y-2">
      <Textarea
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder="Notiz zur Entscheidung (optional)"
        rows={compact ? 2 : 3}
        className="resize-none text-sm"
      />
      <div className="flex flex-wrap gap-2">
        <Button size="sm" variant="success" disabled={busy} onClick={() => act("freigeben")}>
          <CheckCircle2 className="h-4 w-4" /> Freigeben
        </Button>
        <Button size="sm" variant="outline" disabled={busy} onClick={() => act("hinschauen")}>
          <XCircle className="h-4 w-4" /> Hinschauen bestätigen
        </Button>
      </div>
    </div>
  );
}
