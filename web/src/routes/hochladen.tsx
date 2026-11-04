import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useRef, useState } from "react";
import { Upload } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/beleg/page-header";
import { DocThumb } from "@/components/beleg/doc-thumb";
import { useBeleg } from "@/lib/beleg-store";

export const Route = createFileRoute("/hochladen")({
  head: () => ({ meta: [{ title: "Belege hochladen – Beleg-Prüfung" }] }),
  component: Hochladen,
});

function Hochladen() {
  const { upload, loading } = useBeleg();
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);

  const onSubmit = async () => {
    if (!files.length) return;
    setBusy(true);
    try {
      await upload(files);
      setFiles([]);
      void navigate({ to: "/pruefen" });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-2xl space-y-6 animate-rise">
      <PageHeader title="Belege hochladen" description="Neue Rechnungen/Belege hochladen, analysieren und in die Warteschlange einreihen." />

      <Card className="shadow-card">
        <CardContent className="space-y-4 p-6">
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            className="flex w-full flex-col items-center gap-2 rounded-xl border-2 border-dashed p-10 text-center text-muted-foreground transition-colors hover:border-primary hover:text-primary"
          >
            <Upload className="h-7 w-7" />
            <span className="text-sm font-medium">Dateien auswählen</span>
            <span className="text-xs">PDF, JPG, PNG, TIFF, WEBP</span>
          </button>
          <input
            ref={inputRef}
            type="file"
            multiple
            accept=".pdf,.jpg,.jpeg,.png,.tif,.tiff,.webp"
            className="hidden"
            onChange={(e) => setFiles(Array.from(e.target.files ?? []))}
          />

          {files.length > 0 && (
            <div className="flex flex-wrap gap-3">
              {files.map((f, i) => (
                <div key={i} className="w-20 text-center">
                  <DocThumb src={f.type.startsWith("image/") ? URL.createObjectURL(f) : null} alt={f.name} className="h-20 w-20" />
                  <p className="mt-1 truncate text-[11px] text-muted-foreground">{f.name}</p>
                </div>
              ))}
            </div>
          )}

          <Button onClick={onSubmit} disabled={!files.length || busy || loading} className="w-full">
            {busy ? "Lädt hoch …" : `Hochladen & Analysieren${files.length ? ` (${files.length})` : ""}`}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
