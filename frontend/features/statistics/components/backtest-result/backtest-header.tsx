import { ArrowLeft, RotateCcw, Scale } from "lucide-react";
import { Link } from "react-router-dom";
import { BacktestBadge } from "@/shared/components/backtest-badge";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { displayDate, displayMoney, displayMonthSlashYear, parseLocalDate } from "@/shared/lib/utils/display";
import type { BacktestPriceImpact, BacktestResult } from "@/types";

const PRICE_IMPACT_TEXT: Record<BacktestPriceImpact, string> = {
  OFF: "sem impacto de preço",
  REALISTIC: "impacto de preço realista",
  STRONG: "impacto de preço forte",
};

type BacktestHeaderProps = {
  simulationId: number;
  result: BacktestResult;
  /** Só o host roda de novo */
  isHost: boolean;
};

/** Cabeçalho do resultado: o nome, se concluiu ou parou, o período e as regras, com os atalhos para comparar e repetir. */
export function BacktestHeader({ simulationId, result, isHost }: BacktestHeaderProps) {
  const { config, finished, stopped_on: stoppedOn, total_days: total, done_days: done } = result;
  const pregoes = `${done.toLocaleString("pt-BR")} ${done === 1 ? "pregão" : "pregões"}`;
  const period = finished
    ? `${displayMonthSlashYear(config.start_date)} → ${displayMonthSlashYear(config.end_date)} · ${pregoes}`
    : `${displayMonthSlashYear(config.start_date)} → ${displayMonthSlashYear(stoppedOn ?? config.start_date)} · rodou ${done.toLocaleString("pt-BR")} de ${total.toLocaleString("pt-BR")} pregões`;
  const money = `${displayMoney(config.starting_cash)} + ${displayMoney(config.monthly_contribution)} por mês`;

  return (
    <div className="grid gap-3.5">
      <div className="flex">
        <Button variant="outline" size="sm" nativeButton={false} render={<Link to="/lobby" />}>
          <ArrowLeft />
          Voltar ao lobby
        </Button>
      </div>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="grid gap-1">
          <h1 className="flex flex-wrap items-center gap-2.5 text-2xl font-bold">
            {config.name}
            <BacktestBadge />
            {finished ? (
              <Badge variant="success">Concluído</Badge>
            ) : (
              <Badge variant="info">Parado em {stoppedOn ? displayDate(parseLocalDate(stoppedOn)) : "—"}</Badge>
            )}
          </h1>
          <p className="text-sm text-muted-foreground">
            {period} · {money} · {PRICE_IMPACT_TEXT[config.price_impact]}
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            nativeButton={false}
            render={<Link to={`/compare-simulations?ids=${simulationId}`} />}
          >
            <Scale />
            Comparar com outras
          </Button>
          {isHost && (
            <Button nativeButton={false} render={<Link to={`/backtest/new?from=${simulationId}`} />}>
              <RotateCcw />
              Rodar de novo
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
