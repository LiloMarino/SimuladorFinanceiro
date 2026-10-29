import { KeyValueRow } from "@/shared/components/key-value-row";
import { MetricLabel } from "@/shared/components/metric-hint";
import { cn } from "@/shared/lib/utils";
import { displayMoney, displaySignedMoney, displaySignedPercent } from "@/shared/lib/utils/display";
import type { MonthSummary } from "@/types";
import { displayRanking } from "../../lib/summary";
import { MONTH_RETURN, POSITION_RESULT } from "../../lib/summary-metrics";
import { NetworthChange, ReturnComparison } from "./return-comparison";

type MonthSummaryViewProps = { summary: MonthSummary };

/** O mês de um jogador: patrimônio, rentabilidade, posições, caixa e ranking. */
export function MonthSummaryView({ summary }: MonthSummaryViewProps) {
  const best = summary.best_position;
  const worst = summary.worst_position;

  return (
    <div className="grid gap-4">
      <NetworthChange start={summary.networth_start} end={summary.networth_end} />
      <ReturnComparison
        metric={MONTH_RETURN}
        value={summary.return_pct}
        cdi={summary.cdi_pct}
        ibov={summary.ibov_pct}
      />

      {/* Posições */}
      <div className="grid">
        <span className="text-xs font-medium text-muted-foreground">
          <MetricLabel metric={POSITION_RESULT} />
        </span>
        {best ? (
          <>
            <PositionRow label={worst ? "Melhor" : "Única"} position={best} />
            {worst && <PositionRow label="Pior" position={worst} />}
          </>
        ) : (
          <span className="py-1.75 text-[13px] text-muted-foreground">Nenhuma ação na carteira no mês.</span>
        )}
      </div>

      {/* Caixa do mês e ranking */}
      <div className="grid">
        {Number(summary.dividends) > 0 && (
          <KeyValueRow label="Proventos recebidos" value={displayMoney(summary.dividends)} />
        )}
        <KeyValueRow label="IR pago" value={displayMoney(summary.income_tax)} />
        <KeyValueRow label="Aportes" value={displaySignedMoney(summary.contributions)} />
        {summary.ranking && <KeyValueRow label="Ranking" value={displayRanking(summary.ranking)} />}
      </div>
    </div>
  );
}

type PositionRowProps = {
  label: string;
  position: NonNullable<MonthSummary["best_position"]>;
};

function PositionRow({ label, position }: PositionRowProps) {
  const result = Number(position.result);
  return (
    <KeyValueRow
      label={
        <>
          {label}: <b className="font-semibold text-foreground">{position.ticker}</b>
          {position.name !== position.ticker && ` · ${position.name}`}
        </>
      }
      value={
        <>
          {displaySignedMoney(position.result)}
          {position.result_pct !== null && ` (${displaySignedPercent(position.result_pct)})`}
        </>
      }
      valueClassName={cn("font-mono", result > 0 && "text-success", result < 0 && "text-destructive")}
    />
  );
}
