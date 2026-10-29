import type { ReactNode } from "react";
import { InfoHint } from "@/shared/components/info-hint";
import { Badge } from "@/shared/components/ui/badge";
import { cn } from "@/shared/lib/utils";
import { displayMonthSlashYear, displayPercent } from "@/shared/lib/utils/display";
import type { BudgetEffect } from "@/types";
import { effectHeadline, rateChangeLabel, relativeChange, shareLabel } from "../lib/budget";

const TONE_CLASS = { success: "text-success", destructive: "text-destructive", default: "text-foreground" } as const;

function Line({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex items-baseline justify-between gap-3">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="text-right font-mono font-semibold">{children}</dd>
    </div>
  );
}

/** Um "antes → depois" com a variação relativa ao lado, quando existe. */
function Change({ text, relative }: { text: string; relative: string | null }) {
  return (
    <>
      {text}
      {relative && <span className="ml-1 font-normal text-muted-foreground">({relative})</span>}
    </>
  );
}

type MeasureBudgetEffectProps = { effect: BudgetEffect };

/** O que a medida faz com a conta do governo, estimado: receita, resultado e dívida no fim do mandato. */
export function MeasureBudgetEffect({ effect }: MeasureBudgetEffectProps) {
  const headline = effectHeadline(effect);

  return (
    <div className="grid gap-2.5 rounded-lg border border-info-border bg-info-soft/40 p-3.5">
      <div className="flex items-center justify-between gap-3">
        <span className="inline-flex items-center gap-1 text-sm font-medium">
          Efeito no orçamento, estimado
          <InfoHint label="Como ler a estimativa">
            <div className="space-y-1 text-left">
              <p>
                A conta supõe que a medida valha hoje e que mais nada mude até o fim do mandato. O resultado é a receita
                menos o gasto e os juros da dívida, em % do PIB por ano.
              </p>
              <p>
                Ex.: resultado de −4,42% para −4,50% quer dizer que o governo passa a faltar mais 0,08% do PIB por ano.
              </p>
            </div>
          </InfoHint>
        </span>
        <Badge variant="secondary" size="sm">
          a sala vê na fila
        </Badge>
      </div>

      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <span className={cn("font-mono text-[26px] leading-none font-semibold", TONE_CLASS[headline.tone])}>
          {headline.value}
        </span>
        <span className="text-[13px]">{headline.detail}</span>
      </div>

      <dl className="grid gap-1 text-[12.5px]">
        {(effect.rate_before !== null || effect.rate_after !== null) && (
          <Line label={`Alíquota · ${effect.tax_name}`}>
            <Change
              text={rateChangeLabel(effect.rate_before, effect.rate_after)}
              relative={
                effect.rate_before !== null && effect.rate_after !== null
                  ? relativeChange(effect.rate_before, effect.rate_after)
                  : null
              }
            />
          </Line>
        )}
        <Line label={`Receita · ${effect.tax_name}`}>
          <Change
            text={`${shareLabel(effect.tax_revenue_before)} → ${shareLabel(effect.tax_revenue_after)}`}
            relative={relativeChange(effect.tax_revenue_before, effect.tax_revenue_after)}
          />
        </Line>
        <Line label="Resultado do governo, por ano">
          {shareLabel(effect.result_before)} → {shareLabel(effect.result_after)}
        </Line>
        <Line label={`Dívida ÷ PIB em ${displayMonthSlashYear(effect.debt_end)}, se nada mais mudar`}>
          {displayPercent(effect.debt_before, 1)} → {displayPercent(effect.debt_after, 1)}
        </Line>
      </dl>
    </div>
  );
}
