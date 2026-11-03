import { ArrowRight, Info } from "lucide-react";
import { StackedBar } from "@/shared/components/stacked-bar";
import { displayWholePercent } from "@/shared/lib/credit";
import { displayLeverage } from "@/shared/lib/credit-metrics";
import { cn } from "@/shared/lib/utils";
import { displayMoney, displayMonthName } from "@/shared/lib/utils/display";
import type { CreditOverview, LoanQuote } from "@/types";

type SignImpactProps = {
  overview: CreditOverview;
  /** Valor digitado no cartão; a cotação só chega depois do cálculo */
  amount: number;
  quote: LoanQuote | undefined;
};

/** "Se você assinar": dívida, parcelas, alavancagem e sobra do limite, hoje → depois. */
export function SignImpact({ overview, amount, quote }: SignImpactProps) {
  const { offer, loans, rating } = overview;
  const debtLimitAmount = Number(offer.debt_limit_amount);
  const currentDebt = Number(overview.debt);
  const room = Math.max(debtLimitAmount - currentDebt, 0);
  const thisLoan = Math.min(amount, room);
  const spare = room - thisLoan;
  const currentInstallments = loans.reduce((total, loan) => total + Number(loan.installment), 0);

  return (
    <div className="grid gap-3.5 rounded-xl border p-4">
      <div className="flex items-baseline justify-between gap-3">
        <span className="text-sm font-semibold">Se você assinar</span>
        <span className="text-xs text-muted-foreground">hoje → depois</span>
      </div>

      {/* Hoje → depois */}
      <div className="grid grid-cols-2 gap-x-6 gap-y-4">
        <Change label="Dívida" before={displayMoney(currentDebt)} after={displayMoney(currentDebt + amount)} />
        <Change
          label="Parcelas por mês"
          before={displayMoney(currentInstallments)}
          after={quote ? displayMoney(currentInstallments + Number(quote.installment)) : undefined}
        />
        <Change
          label="Alavancagem"
          before={quote ? displayLeverage(quote.leverage_before) : displayLeverage(overview.leverage)}
          after={quote ? displayLeverage(quote.leverage_after) : undefined}
        />
        <Change label="Sobra do limite" before={displayMoney(room)} after={displayMoney(spare)} />
      </div>

      {/* Limite de dívida */}
      <div className="grid gap-1.5">
        <div className="flex justify-between gap-3 text-[13px]">
          <span className="font-medium">Limite de dívida</span>
          <span className="font-mono text-muted-foreground">
            {displayMoney(debtLimitAmount)} · {displayWholePercent(offer.debt_limit)} do patrimônio
          </span>
        </div>
        <StackedBar
          size="lg"
          segments={[
            { key: "today", fraction: fractionOf(currentDebt, debtLimitAmount), color: "bg-primary" },
            { key: "loan", fraction: fractionOf(thisLoan, debtLimitAmount), color: "bg-info-border" },
            { key: "spare", fraction: fractionOf(spare, debtLimitAmount), color: "bg-transparent" },
          ]}
        />
        <ul className="flex flex-wrap gap-x-3.5 gap-y-1 text-xs text-muted-foreground">
          <LimitLegend color="bg-primary" label="Dívida de hoje" value={currentDebt} />
          <LimitLegend color="bg-info-border" label="Este empréstimo" value={amount} />
          <LimitLegend color="bg-muted" label="Sobra" value={spare} />
        </ul>
      </div>

      <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <Info className="size-3.5" aria-hidden="true" />A alavancagem entra na nota de risco, recalculada no fim de{" "}
        {displayMonthName(rating.next_review)}.
      </span>
    </div>
  );
}

function Change({ label, before, after }: { label: string; before: string; after: string | undefined }) {
  return (
    <div className="grid gap-1">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <span className="font-mono text-[13px] text-muted-foreground">{before}</span>
      <span className="flex items-center gap-1.5">
        <ArrowRight className="size-3.5 text-faint-foreground" aria-hidden="true" />
        <span className="font-mono text-[17px] font-semibold">{after ?? "—"}</span>
      </span>
    </div>
  );
}

function fractionOf(part: number, whole: number) {
  return whole > 0 ? Math.min(part / whole, 1) : 0;
}

function LimitLegend({ color, label, value }: { color: string; label: string; value: number }) {
  return (
    <li className="flex items-center gap-1.5">
      <span className={cn("size-2.5 rounded-[3px]", color)} aria-hidden="true" />
      {label} <span className="font-mono">{displayMoney(value)}</span>
    </li>
  );
}
