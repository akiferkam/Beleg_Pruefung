import { createFileRoute, Link } from "@tanstack/react-router";
import { AlertTriangle, ArrowRight, CheckCircle2, Database, FileStack, SlidersHorizontal, Upload, UserRound, XCircle } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, XAxis, YAxis } from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent, type ChartConfig } from "@/components/ui/chart";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/components/beleg/page-header";
import { RunBar } from "@/components/beleg/run-bar";
import { displayStatus } from "@/components/beleg/status";
import { CHECK_GROUPS, dateTimeDe, eur, useBeleg, type ActivityKind } from "@/lib/beleg-store";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Übersicht – Beleg-Prüfung" },
      { name: "description", content: "Kennzahlen, Prüfstatistik und letzte Aktivitäten der Belegprüfung." },
      { property: "og:title", content: "Übersicht – Beleg-Prüfung" },
      { property: "og:description", content: "Kennzahlen, Prüfstatistik und letzte Aktivitäten der Belegprüfung." },
    ],
  }),
  component: Dashboard,
});

const ACTIVITY_ICON: Record<ActivityKind, typeof Upload> = {
  analyse: FileStack,
  commit: Database,
  manuell: UserRound,
  upload: Upload,
  policy: SlidersHorizontal,
};

function Dashboard() {
  const { docs, run, activity } = useBeleg();
  const counts = {
    total: docs.length,
    auto: docs.filter((d) => !d.manual && d.autoDecision === "freigeben").length,
    queue: docs.filter((d) => displayStatus(d) === "zu-pruefen").length,
    rejected: docs.filter((d) => displayStatus(d) === "beanstandet").length,
    manualFree: docs.filter((d) => d.manual?.entscheidung === "freigeben").length,
  };
  const volume = docs.reduce((s, d) => s + (d.grossAmount ?? 0), 0);

  const byGroup = Object.entries(CHECK_GROUPS).map(([key, label]) => ({
    key,
    label,
    count: docs.reduce((s, d) => s + d.blockingReasons.filter((r) => r.id.startsWith(key)).length, 0),
  }));
  const pie = [
    { name: "Automatisch freigegeben", value: counts.auto, fill: "var(--color-auto)" },
    { name: "Manuell freigegeben", value: counts.manualFree, fill: "var(--color-manual)" },
    { name: "Zu prüfen", value: counts.queue, fill: "var(--color-queue)" },
    { name: "Beanstandet", value: counts.rejected, fill: "var(--color-rejected)" },
  ];
  const pieConfig = {
    auto: { label: "Automatisch freigegeben", color: "var(--success)" },
    manual: { label: "Manuell freigegeben", color: "var(--chart-1)" },
    queue: { label: "Zu prüfen", color: "var(--warning)" },
    rejected: { label: "Beanstandet", color: "var(--danger)" },
  } satisfies ChartConfig;
  const barConfig = { count: { label: "Befunde", color: "var(--chart-1)" } } satisfies ChartConfig;

  const kpis = [
    { label: "Belege verarbeitet", value: counts.total, sub: `Volumen ${eur(volume)}`, Icon: FileStack, tone: "bg-accent text-accent-foreground" },
    { label: "Automatisch freigegeben", value: counts.auto, sub: `${counts.total ? Math.round((counts.auto / counts.total) * 100) : 0} % Dunkelverarbeitung`, Icon: CheckCircle2, tone: "bg-success-soft text-success" },
    { label: "Manuelle Prüfung nötig", value: counts.queue, sub: "offen in der Warteschlange", Icon: AlertTriangle, tone: "bg-warning-soft text-warning" },
    { label: "Beanstandet", value: counts.rejected, sub: `${counts.manualFree} manuell freigegeben`, Icon: XCircle, tone: "bg-danger-soft text-danger" },
  ];

  return (
    <div className="space-y-6 animate-rise">
      <PageHeader
        title="Übersicht"
        description="Das System filtert vor, der Mensch entscheidet: Jeder Beleg wird deterministisch gegen den Prüfkatalog A–F geprüft."
        actions={
          <Button asChild>
            <Link to="/pruefen">
              Warteschlange öffnen <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        }
      />
      <RunBar />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map((k) => (
          <Card key={k.label} className="shadow-card">
            <CardContent className="p-5">
              <div className="flex items-start justify-between">
                <p className="text-sm text-muted-foreground">{k.label}</p>
                <span className={`flex h-8 w-8 items-center justify-center rounded-lg ${k.tone}`}>
                  <k.Icon className="h-4 w-4" />
                </span>
              </div>
              {run ? <p className="tabular mt-2 text-3xl font-semibold">{k.value}</p> : <Skeleton className="mt-2 h-9 w-16" />}
              <p className="mt-1 text-xs text-muted-foreground">{k.sub}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        <Card className="shadow-card lg:col-span-3">
          <CardHeader>
            <CardTitle className="text-base">Befunde nach Prüfbereich</CardTitle>
            <CardDescription>Blockierende Prüfpunkte im aktuellen Lauf</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={barConfig} className="h-64 w-full">
              <BarChart data={byGroup} layout="vertical" margin={{ left: 8, right: 16 }}>
                <CartesianGrid horizontal={false} strokeDasharray="3 3" />
                <XAxis type="number" allowDecimals={false} tickLine={false} axisLine={false} />
                <YAxis type="category" dataKey="label" width={190} tickLine={false} axisLine={false} fontSize={12} />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar dataKey="count" fill="var(--color-count)" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ChartContainer>
          </CardContent>
        </Card>
        <Card className="shadow-card lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Entscheidungen</CardTitle>
            <CardDescription>Verteilung aller {counts.total} Belege</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={pieConfig} className="mx-auto h-48 w-full">
              <PieChart>
                <ChartTooltip content={<ChartTooltipContent hideLabel />} />
                <Pie data={pie} dataKey="value" nameKey="name" innerRadius={52} outerRadius={80} strokeWidth={2}>
                  {pie.map((p) => (
                    <Cell key={p.name} fill={p.fill} />
                  ))}
                </Pie>
              </PieChart>
            </ChartContainer>
            <ul className="mt-3 grid grid-cols-2 gap-2 text-xs">
              {pie.map((p, i) => (
                <li key={p.name} className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-sm" style={{ background: Object.values(pieConfig)[i].color }} />
                  <span className="text-muted-foreground">{p.name}</span>
                  <span className="tabular ml-auto font-medium">{p.value}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      <Card className="shadow-card">
        <CardHeader>
          <CardTitle className="text-base">Letzte Aktivitäten</CardTitle>
          <CardDescription>Uploads, manuelle Entscheidungen, Regeländerungen und Ledger-Übernahmen</CardDescription>
        </CardHeader>
        <CardContent>
          {activity.length === 0 ? (
            <p className="py-6 text-center text-sm text-muted-foreground">
              Noch keine Aktivitäten. Öffnen Sie die Warteschlange, um Belege zu entscheiden.
            </p>
          ) : (
            <ul className="divide-y">
              {activity.slice(0, 8).map((a) => {
                const Icon = ACTIVITY_ICON[a.kind];
                return (
                  <li key={a.id} className="flex items-center gap-3 py-3">
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted text-muted-foreground">
                      <Icon className="h-4 w-4" />
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium">
                        {a.docId ? (
                          <Link to="/belege/$docId" params={{ docId: a.docId }} className="hover:underline">
                            {a.title}
                          </Link>
                        ) : (
                          a.title
                        )}
                      </p>
                      {a.detail && <p className="truncate text-xs text-muted-foreground">{a.detail}</p>}
                    </div>
                    <span className="tabular shrink-0 text-xs text-muted-foreground">{dateTimeDe(a.at)}</span>
                  </li>
                );
              })}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
