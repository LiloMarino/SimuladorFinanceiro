import type { CSSProperties } from "react";
import { Badge } from "@/shared/components/ui/badge";
import { Progress } from "@/shared/components/ui/progress";
import { cn } from "@/shared/lib/utils";
import { displaySignedPercent } from "@/shared/lib/utils/display";
import type { CandlePattern, PatternStats } from "@/types";
import { PATTERN_INFO, SIDE_LABEL } from "../../lib/candle-patterns";
import { displayPatternDays, hitRate } from "../../lib/pattern-view";
import { PatternDrawing } from "./pattern-drawing";

interface PatternCardProps {
  ticker: string;
  pattern: CandlePattern;
  stats: PatternStats;
  /** O padrão fecha hoje; o dia vem escrito como "Hoje". */
  today: boolean;
  /** O desafio deste padrão ainda espera resposta. */
  challengeOpen: boolean;
  className?: string;
  style?: CSSProperties;
}

/** O que o padrão é, o que sugere e quanto o histórico do ativo deu razão a ele. */
export function PatternCard({ ticker, pattern, stats, today, challengeOpen, className, style }: PatternCardProps) {
  const info = PATTERN_INFO[pattern.code];
  const side = SIDE_LABEL[pattern.direction];
  const days = displayPatternDays(pattern);

  return (
    <div
      className={cn("grid gap-2.5 rounded-xl border bg-popover p-3.5 text-[13px] shadow-lg", className)}
      style={style}
    >
      {/* Cabeçalho */}
      <div className="flex items-start gap-3">
        <PatternDrawing key={pattern.code} code={pattern.code} />
        <div className="grid min-w-0 gap-1">
          <div className="flex flex-wrap items-center gap-2">
            <p className="text-[15px] font-semibold">{info.name}</p>
            <Badge variant={badgeVariant(pattern.direction)} size="sm">
              {side.card}
            </Badge>
          </div>
          <span className="text-xs text-muted-foreground">
            {today ? `Hoje, ${days}` : days} · {ticker}
          </span>
        </div>
      </div>
      <span>{info.summary}</span>

      {pattern.direction !== "neutral" && <HistoryBlock ticker={ticker} stats={stats} side={pattern.direction} />}

      {/* Desta vez */}
      <div className="flex items-center justify-between border-t pt-2">
        <span className="text-xs font-medium text-muted-foreground">Desta vez</span>
        <ThisTime pattern={pattern} challengeOpen={challengeOpen} />
      </div>
    </div>
  );
}

function badgeVariant(side: CandlePattern["direction"]) {
  if (side === "up") return "success";
  if (side === "down") return "destructive";
  return "secondary";
}

interface HistoryBlockProps {
  ticker: string;
  stats: PatternStats;
  side: "up" | "down";
}

/** "E se ele acertou?": a taxa do histórico, ou o aviso de amostra pequena. */
function HistoryBlock({ ticker, stats, side }: HistoryBlockProps) {
  const rate = hitRate(stats);
  const went = side === "up" ? "subiu" : "caiu";

  if (rate === null) {
    return (
      <div className="grid gap-1">
        <span className="text-xs font-medium text-muted-foreground">E se ele acertou?</span>
        {stats.checked === 0 ? (
          <span>Ainda não houve uma ocorrência deste padrão com os 5 pregões seguintes no histórico da {ticker}.</span>
        ) : (
          <>
            <span>
              Apareceu só <b className="font-mono">{stats.checked}</b> {stats.checked === 1 ? "vez" : "vezes"} no
              histórico da {ticker}: pouco para dizer se costuma acertar.
            </span>
            <span className="text-xs text-muted-foreground">
              Em{" "}
              <b className="font-mono">
                {stats.hits} de {stats.checked}
              </b>{" "}
              o preço {went} nos 5 pregões seguintes.
            </span>
          </>
        )}
      </div>
    );
  }

  const misses = stats.checked - stats.hits;
  return (
    <div className="grid gap-1.5">
      <span className="text-xs font-medium text-muted-foreground">E se ele acertou?</span>
      <span>
        No histórico da {ticker} até hoje, apareceu <b className="font-mono">{displayCount(stats.checked)}</b> vezes; em{" "}
        <b className="font-mono">{displayCount(stats.hits)}</b> o preço {went} nos 5 pregões seguintes.
      </span>
      <div className="flex items-center gap-2">
        <Progress
          className="flex-1"
          value={rate * 100}
          size="sm"
          indicatorTone="success"
          aria-label="Taxa de acerto do padrão"
        />
        <span className="font-mono text-xs font-semibold">
          {Math.round(rate * 100)}% de {displayCount(stats.checked)}
        </span>
      </div>
      <span className="text-xs text-muted-foreground">
        Padrão não é garantia: nas outras {displayCount(misses)} vezes, o preço foi para o outro lado.
      </span>
    </div>
  );
}

const displayCount = (value: number) => new Intl.NumberFormat("pt-BR").format(value);

function ThisTime({ pattern, challengeOpen }: { pattern: CandlePattern; challengeOpen: boolean }) {
  if (challengeOpen)
    return (
      <Badge variant="info" size="sm">
        Desafio aberto · responda acima
      </Badge>
    );
  if (pattern.change_5d === null) {
    return <span className="text-xs text-muted-foreground">ainda faltam pregões para conferir</span>;
  }
  return (
    <span
      className={cn(
        "font-mono text-[13px] font-semibold",
        pattern.change_5d > 0 && "text-success",
        pattern.change_5d < 0 && "text-destructive",
      )}
    >
      {displaySignedPercent(pattern.change_5d, 1)} em 5 pregões
    </span>
  );
}
