import type { ReactNode } from "react";
import { Avatar, AvatarFallback } from "@/shared/components/ui/avatar";
import { Card } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { MetricHint } from "@/shared/components/metric-hint";
import type { MetricInfo } from "@/shared/lib/metric-info";
import { cn } from "@/shared/lib/utils";
import {
  displayMoney,
  displayMonthSlashYear,
  displayNumber,
  displayPercent,
  displaySignedPercent,
} from "@/shared/lib/utils/display";
import type { Highlights } from "@/types";
import { useStatisticsReport } from "../../hooks/queries/useStatisticsReport";
import { CUMULATIVE_RETURN, INCOME_TAX_PAID, MAX_DRAWDOWN } from "../../lib/metrics";

interface HighlightProps {
  label: string;
  metric?: MetricInfo;
  value: ReactNode;
  tone?: "positive" | "negative";
  player: string | undefined;
  color: string;
}

function Highlight({ label, metric, value, tone, player, color }: HighlightProps) {
  return (
    <Card size="sm">
      <div className="grid gap-1.5 px-4">
        <span className="flex items-center gap-1 text-xs font-medium text-muted-foreground">
          {label}
          {metric && <MetricHint metric={metric} />}
        </span>
        <span
          className={cn(
            "font-mono text-lg font-semibold",
            tone === "positive" && "text-success",
            tone === "negative" && "text-destructive",
          )}
        >
          {player ? value : "—"}
        </span>
        <span className="flex items-center gap-1.5 text-xs">
          {player ? (
            <>
              <Avatar size="sm">
                <AvatarFallback color={color}>{player.charAt(0).toUpperCase()}</AvatarFallback>
              </Avatar>
              {player}
            </>
          ) : (
            <span className="text-muted-foreground">Ninguém nesta partida</span>
          )}
        </span>
      </div>
    </Card>
  );
}

// Zero fica neutro: nem ganhou nem perdeu
function toneOf(value: string | undefined) {
  if (value === undefined || Number(value) === 0) return undefined;
  return Number(value) > 0 ? "positive" : "negative";
}

interface HighlightsRowProps {
  simulationId: number;
  currentPlayerName?: string;
  colorOf: (label: string) => string;
}

/** Quem foi melhor em quê na partida, e o seu melhor mês. */
export function HighlightsRow({ simulationId, currentPlayerName, colorOf }: HighlightsRowProps) {
  const { data } = useStatisticsReport("highlights", [simulationId]);
  if (!data) return <HighlightsSkeleton />;

  const item = (h: Highlights["biggest_return"]) => ({
    player: h?.player_nickname,
    color: colorOf(h?.player_nickname ?? ""),
  });
  const best = data.your_best_month;

  return (
    <div className="grid gap-3.5 sm:grid-cols-2 lg:grid-cols-5">
      <Highlight
        label="Maior retorno"
        metric={CUMULATIVE_RETURN}
        value={data.biggest_return && displaySignedPercent(data.biggest_return.value)}
        tone={toneOf(data.biggest_return?.value)}
        {...item(data.biggest_return)}
      />
      <Highlight
        label="Menor queda"
        metric={MAX_DRAWDOWN}
        value={data.smallest_drawdown && displayPercent(data.smallest_drawdown.value)}
        {...item(data.smallest_drawdown)}
      />
      <Highlight
        label="Mais negócios"
        value={data.most_trades && displayNumber(data.most_trades.value, 0)}
        {...item(data.most_trades)}
      />
      <Highlight
        label="Mais IR pago"
        metric={INCOME_TAX_PAID}
        value={data.most_tax && displayMoney(data.most_tax.value)}
        {...item(data.most_tax)}
      />
      <Highlight
        label="Seu melhor mês"
        value={best && `${displaySignedPercent(best.value)} · ${displayMonthSlashYear(best.month)}`}
        tone={toneOf(best?.value)}
        player={best ? currentPlayerName : undefined}
        color={colorOf(currentPlayerName ?? "")}
      />
    </div>
  );
}

export function HighlightsSkeleton() {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
      {Array.from({ length: 5 }, (_, i) => (
        <Skeleton key={i} className="h-[76px]" />
      ))}
    </div>
  );
}
