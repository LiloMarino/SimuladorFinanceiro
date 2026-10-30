import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { cn } from "@/shared/lib/utils";
import { displaySignedPercent } from "@/shared/lib/utils/display";
import type { CandlePattern } from "@/types";
import { PATTERN_INFO, SIDE_LABEL } from "../../lib/candle-patterns";
import { loadListOpen, saveListOpen } from "../../lib/pattern-list-preference";
import { displayPatternDays, periodScore } from "../../lib/pattern-view";

interface PatternListProps {
  patterns: CandlePattern[];
  /** O dia final do padrão em destaque (o que o card mostra). */
  activeDay: string | null;
  onSelect: (pattern: CandlePattern) => void;
}

/** Os padrões do período, em seção recolhível embaixo do gráfico. */
export function PatternList({ patterns, activeDay, onSelect }: PatternListProps) {
  const [open, setOpen] = useState(loadListOpen);
  const score = periodScore(patterns);
  const scoreText =
    score.checked > 0 ? `${score.hits} de ${score.checked} acertaram` : "Nenhum padrão com os 5 pregões conferidos";
  const toggle = () => {
    saveListOpen(!open);
    setOpen(!open);
  };

  return (
    <section className="grid border-t pt-2">
      {/* Cabeçalho */}
      <button
        type="button"
        aria-expanded={open}
        onClick={toggle}
        className="flex items-center justify-between gap-2 rounded-md px-2.5 py-1.5 text-left hover:bg-subtle"
      >
        <span className="flex items-center gap-1.5 text-[13px] font-semibold">
          <ChevronDown className={cn("size-4 transition-transform", !open && "-rotate-90")} />
          Padrões neste período · {patterns.length}
        </span>
        <span className="text-xs text-muted-foreground">
          {open ? "5 pregões depois" : score.checked > 0 ? scoreText : ""}
        </span>
      </button>

      {/* Linhas */}
      {open && (
        <>
          <ul className="grid">
            {patterns.map((pattern) => (
              <li key={`${pattern.code}:${pattern.end}`}>
                <button
                  type="button"
                  onClick={() => onSelect(pattern)}
                  className={cn(
                    "grid w-full grid-cols-[84px_minmax(0,1fr)_auto] items-center gap-2 rounded-md px-2.5 py-1.5 text-left text-[13px] hover:bg-subtle",
                    pattern.end === activeDay && "bg-info-soft hover:bg-info-soft",
                  )}
                >
                  <span className="font-mono text-xs text-muted-foreground">{displayPatternDays(pattern)}</span>
                  <span className="flex min-w-0 items-center gap-1.5 font-medium">
                    <Badge variant={chipVariant(pattern.direction)} size="sm">
                      {SIDE_LABEL[pattern.direction].list}
                    </Badge>
                    <span className="truncate">{PATTERN_INFO[pattern.code].name}</span>
                  </span>
                  <Outcome pattern={pattern} />
                </button>
              </li>
            ))}
          </ul>
          <span className="px-2.5 pt-1.5 text-xs text-muted-foreground">
            {scoreText}
            {patterns.some((pattern) => pattern.direction === "neutral") && " · o doji não aposta em lado"}
          </span>
        </>
      )}
    </section>
  );
}

function chipVariant(side: CandlePattern["direction"]) {
  if (side === "up") return "success";
  if (side === "down") return "destructive";
  return "secondary";
}

function Outcome({ pattern }: { pattern: CandlePattern }) {
  if (pattern.change_5d === null) {
    return <span className="text-right text-xs text-muted-foreground">confere em breve</span>;
  }
  return (
    <span className="flex items-center justify-end gap-1.5 text-right">
      <span
        className={cn(
          "font-mono text-xs",
          pattern.change_5d > 0 && "text-success",
          pattern.change_5d < 0 && "text-destructive",
        )}
      >
        {displaySignedPercent(pattern.change_5d, 1)}
      </span>
      {pattern.hit !== null && (
        <span
          className={pattern.hit ? "text-success" : "text-destructive"}
          aria-label={pattern.hit ? "acertou" : "errou"}
        >
          {pattern.hit ? "✓" : "✕"}
        </span>
      )}
    </span>
  );
}
