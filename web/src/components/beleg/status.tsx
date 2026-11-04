import { CheckCircle2, AlertTriangle, XCircle, Bot, UserRound } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { BelegResult } from "@/lib/api";

export type DisplayStatus = "freigegeben" | "zu-pruefen" | "beanstandet";

export function displayStatus(doc: BelegResult): DisplayStatus {
  if (doc.manual) return doc.manual.entscheidung === "freigeben" ? "freigegeben" : "beanstandet";
  return doc.autoDecision === "freigeben" ? "freigegeben" : "zu-pruefen";
}

const MAP = {
  freigegeben: { label: "Freigegeben", variant: "success" as const, Icon: CheckCircle2 },
  "zu-pruefen": { label: "Zu prüfen", variant: "warning" as const, Icon: AlertTriangle },
  beanstandet: { label: "Beanstandet", variant: "danger" as const, Icon: XCircle },
};

export function StatusBadge({ doc, status }: { doc?: BelegResult; status?: DisplayStatus }) {
  const s = MAP[status ?? displayStatus(doc!)];
  return (
    <Badge variant={s.variant} className="gap-1">
      <s.Icon className="h-3.5 w-3.5" />
      {s.label}
    </Badge>
  );
}

export function SourceBadge({ doc }: { doc: BelegResult }) {
  return doc.manual ? (
    <Badge variant="muted" className="gap-1">
      <UserRound className="h-3 w-3" /> manuell
    </Badge>
  ) : (
    <Badge variant="muted" className="gap-1">
      <Bot className="h-3 w-3" /> automatisch
    </Badge>
  );
}

export function CheckCode({ id }: { id: string }) {
  return (
    <span className="tabular inline-flex h-5 min-w-8 items-center justify-center rounded bg-muted px-1.5 text-[11px] font-medium text-muted-foreground">
      {id}
    </span>
  );
}
