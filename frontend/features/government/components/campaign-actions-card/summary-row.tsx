import { cn } from "@/shared/lib/utils";

export function SummaryRow({
  label,
  tone,
  children,
}: {
  label: string;
  tone?: "up" | "down";
  children: React.ReactNode;
}) {
  return (
    <div className="flex justify-between gap-3">
      <span className="text-muted-foreground">{label}</span>
      <span
        className={cn(
          "text-right font-mono font-semibold",
          tone === "up" && "text-success",
          tone === "down" && "text-destructive",
        )}
      >
        {children}
      </span>
    </div>
  );
}
