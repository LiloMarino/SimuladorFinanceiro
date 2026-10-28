import { cn } from "@/shared/lib/utils";

export type StackedBarSegment = {
  key: string;
  /** Fração do total (0.4 = 40%) */
  fraction: number;
  /** Cor do trecho, como classe de fundo ("bg-chart-1") */
  color?: string;
  /** Cor do trecho como valor CSS, quando ela vem do dado (a cor de um partido) */
  fill?: string;
};

/** Barra empilhada: cada trecho ocupa a sua fração do total. */
export function StackedBar({ segments, className }: { segments: StackedBarSegment[]; className?: string }) {
  return (
    <div role="presentation" className={cn("flex h-2.5 gap-0.5 overflow-hidden rounded-full bg-muted", className)}>
      {segments.map((segment) => (
        <span
          key={segment.key}
          className={segment.color}
          style={{ width: `${segment.fraction * 100}%`, backgroundColor: segment.fill }}
        />
      ))}
    </div>
  );
}
