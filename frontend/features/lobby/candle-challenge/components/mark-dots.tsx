import { cn } from "@/shared/lib/utils";
import type { ChallengeMark } from "@/types";

const LABEL: Record<ChallengeMark, string> = { hit: "acertou", miss: "errou", none: "não respondeu" };

/** Uma bolinha por pergunta: verde acertou, vermelha errou, cinza não respondeu, vazia antes de entrar. */
export function MarkDots({ marks, total }: { marks: (ChallengeMark | null)[]; total: number }) {
  return (
    <span
      className="inline-flex gap-1"
      role="img"
      aria-label={marks.map((mark, i) => `${i + 1}: ${mark ? LABEL[mark] : "ainda não estava"}`).join(", ")}
    >
      {Array.from({ length: total }, (_, index) => {
        const mark = marks[index] ?? null;
        return (
          <i
            key={index}
            className={cn(
              "size-2.5 rounded-full",
              mark === "hit" && "bg-success",
              mark === "miss" && "bg-destructive",
              mark === "none" && "bg-faint-foreground/60",
              mark === null && "border border-dashed border-border",
            )}
          />
        );
      })}
    </span>
  );
}
