import { Info } from "lucide-react";
import { Kpi } from "@/shared/components/kpi";
import { MetricLabel } from "@/shared/components/metric-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import { POLICY_LABEL } from "@/shared/lib/state-company";
import { displayMoney, displayNumber, displayPercent } from "@/shared/lib/utils/display";
import type { StateCompanyDetail } from "@/types";
import { currentPayout, dividendYield, settledMonths } from "../../lib/state-company";
import { STATE_BETA, STATE_DIVIDEND_POLICY, STATE_DIVIDENDS, STATE_FAIR_VALUE } from "../../lib/state-company-metrics";

const EMPTY = "—";

/** A nota dos dividendos: quantos meses somam e quanto isso rende sobre o preço. */
function dividendsNote(company: StateCompanyDetail) {
  const months = settledMonths(company.months).length;
  if (months === 0) return "ainda sem mês fechado";
  const yieldOnPrice = dividendYield(company);
  const period = `em ${months} ${months === 1 ? "mês" : "meses"}`;
  return yieldOnPrice === null ? period : `${period} · ${displayPercent(yieldOnPrice, 1)} do preço`;
}

/** O beta e o que ele quer dizer num dia em que a bolsa cai 2%. */
function betaNote(beta: number) {
  return `a bolsa cai 2%, ela cai ${displayNumber(beta * 2, 1)}%`;
}

/** Os números da estatal: preço, valor justo, dividendos, política e beta; a importada mostra só os três que ela tem. */
export function StateCompanyMetricsRow({ company }: { company: StateCompanyDetail }) {
  const imported = company.origin === "IMPORTED";
  const policy = company.dividend_policy;

  return (
    <Card>
      <CardContent>
        <div className="grid gap-4">
          <div className="grid grid-cols-2 gap-x-6 gap-y-5 md:grid-cols-3 xl:grid-cols-5">
            {/* Preço */}
            <Kpi
              label="Preço no mercado"
              value={company.price === null ? EMPTY : displayMoney(company.price)}
              note={imported ? "o da história × controle de preço" : "fechamento de hoje"}
            />

            {/* Valor justo */}
            {company.fair_value !== null && (
              <Kpi
                label={<MetricLabel metric={STATE_FAIR_VALUE} />}
                value={displayMoney(company.fair_value)}
                note={STATE_FAIR_VALUE.description}
              />
            )}

            {/* Dividendos */}
            <Kpi
              label={<MetricLabel metric={STATE_DIVIDENDS} />}
              value={displayMoney(company.dividends)}
              note={imported ? "12 meses da história × política" : dividendsNote(company)}
            />

            {/* Política */}
            <Kpi
              label={<MetricLabel metric={STATE_DIVIDEND_POLICY} />}
              value={POLICY_LABEL[policy]}
              note={
                imported
                  ? "multiplica os proventos da história"
                  : `paga ${displayPercent(currentPayout(company) ?? 0, 0)} do lucro do mês`
              }
            />

            {/* Beta */}
            {company.beta !== null && (
              <Kpi
                label={<MetricLabel metric={STATE_BETA} />}
                value={displayNumber(company.beta, 1)}
                note={betaNote(Number(company.beta))}
              />
            )}
          </div>

          {/* Nota da importada */}
          {imported && (
            <p className="flex items-start gap-2.5 rounded-md bg-muted px-2.5 py-1 text-xs text-muted-foreground">
              <Info className="mt-0.5 size-3.5 shrink-0" />
              Estatal que já existia segue o preço e os proventos da história, com o controle de preço e a política de
              dividendos do governo como multiplicadores. As três camadas do preço (tendência do ano ligada ao PIB,
              sensibilidade de 0,8 à bolsa e ruído próprio) valem para a estatal fundada na partida.
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
