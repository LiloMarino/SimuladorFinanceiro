import { MetricHint } from "@/shared/components/metric-hint";
import { useLifeStatus } from "@/shared/hooks/queries/useLifeStatus";
import { displayRatePercent } from "@/shared/lib/financial-independence";
import { OVERDRAFT } from "@/shared/lib/life-metrics";
import { displayMoney, displaySignedMoney } from "@/shared/lib/utils/display";

type TopbarCashProps = {
  /** Caixa de hoje; indefinido antes do primeiro dado */
  cash: string | undefined;
  /** Só o viver de renda tem caixa negativo (cheque especial) */
  independence: boolean;
};

/** Caixa disponível; no viver de renda, caixa negativo vira "Cheque especial" com o juro. */
export function TopbarCash({ cash, independence }: TopbarCashProps) {
  const { data: status } = useLifeStatus();
  const overdraft = independence && cash !== undefined && Number(cash) < 0;

  if (!overdraft) {
    return (
      <div className="grid border-l border-border pl-4">
        <span className="text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
          Caixa disponível
        </span>
        <span className="font-mono text-[15px] font-semibold">{cash !== undefined ? displayMoney(cash) : "—"}</span>
      </div>
    );
  }

  return (
    <div className="grid justify-items-end border-l border-border pl-4">
      <span className="flex items-center gap-1 text-[11px] font-semibold tracking-[.06em] text-destructive uppercase">
        {OVERDRAFT.label}
        <MetricHint metric={OVERDRAFT} />
      </span>
      <span className="font-mono text-[15px] font-semibold text-destructive">{displaySignedMoney(cash)}</span>
      {status && (
        <span className="text-[11px] text-destructive">
          {displayRatePercent(status.overdraft_monthly_rate)} ao mês até cobrir
        </span>
      )}
    </div>
  );
}
