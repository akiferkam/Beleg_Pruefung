import { FileText } from "lucide-react";
import { cn } from "@/lib/utils";

export function DocThumb({ src, alt, className }: { src: string | null; alt: string; className?: string }) {
  return (
    <div className={cn("relative overflow-hidden rounded-lg border bg-muted", className)}>
      {src ? (
        <img src={src} alt={alt} loading="lazy" className="h-full w-full object-cover object-top" />
      ) : (
        <div className="flex h-full w-full items-center justify-center text-muted-foreground">
          <FileText className="h-6 w-6" />
        </div>
      )}
    </div>
  );
}
