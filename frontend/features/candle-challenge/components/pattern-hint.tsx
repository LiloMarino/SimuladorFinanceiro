import { PatternDrawing } from "@/features/variable-income/components/candle-patterns/pattern-drawing";
import { PATTERN_INFO, SIDE_LABEL } from "@/features/variable-income/lib/candle-patterns";
import { hitRate } from "@/features/variable-income/lib/pattern-view";
import { Badge } from "@/shared/components/ui/badge";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/shared/components/ui/hover-card";
import type { CandlePatternCode, PatternStats } from "@/types";

const count = (value: number) => new Intl.NumberFormat("pt-BR").format(value);

interface PatternHintProps {
  code: CandlePatternCode;
  stats: PatternStats;
}

/** O nome do padrão, sublinhado: passar o mouse ou focar abre o desenho, o que significa e quanto acertou na base. */
export function PatternHint({ code, stats }: PatternHintProps) {
  const info = PATTERN_INFO[code];
  const side = info.side === "neutral" ? null : info.side;
  const rate = hitRate(stats);

  return (
    <HoverCard>
      {/* oxlint-disable-next-line jsx-a11y/control-has-associated-label */}
      <HoverCardTrigger term render={<button type="button" />}>
        {info.name}
      </HoverCardTrigger>
      <HoverCardContent compact className="w-85">
        <div className="flex items-center gap-2">
          <b className="text-[15px]">{info.name}</b>
          <Badge variant={side === "up" ? "success" : "destructive"} size="sm">
            {SIDE_LABEL[info.side].card}
          </Badge>
        </div>
        <div className="flex justify-center rounded-lg bg-subtle py-1.5">
          <PatternDrawing code={code} />
        </div>
        <span className="text-[13px] leading-normal">{info.summary}</span>
        {side && (
          <span className="rounded-lg bg-subtle px-3 py-2 text-xs text-muted-foreground">
            {rate === null ? (
              <>Ainda são poucos casos na base para dizer se costuma acertar.</>
            ) : (
              <>
                Na base, quando o padrão {info.name} aparece, o preço {side === "up" ? "subiu" : "caiu"} nos 5 pregões
                seguintes em <b className="font-mono text-foreground">{Math.round(rate * 100)}%</b> das vezes (
                <span className="font-mono">{count(stats.checked)}</span> casos). Padrão não é garantia.
              </>
            )}
          </span>
        )}
      </HoverCardContent>
    </HoverCard>
  );
}
