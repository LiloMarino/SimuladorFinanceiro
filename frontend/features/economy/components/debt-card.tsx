import { Link } from "react-router-dom";
import { InfoHint } from "@/shared/components/info-hint";
import { MetricHint } from "@/shared/components/metric-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import { DEBT_GDP, RISK_PREMIUM } from "@/shared/lib/budget-metrics";
import { cn } from "@/shared/lib/utils";
import { displayMoneyLarge, displayPercent } from "@/shared/lib/utils/display";
import type { EconomyPanel } from "@/types";
import { economyRows, stabilizingNote } from "../lib/economy";
import { DEBT_CAUSES, DEBT_RATE, STABILIZING_PRIMARY } from "../lib/economy-metrics";
import { SeriesChart } from "./series-chart";

type DebtCardProps = {
  panel: EconomyPanel;
  /** A dívida e o PIB do último fechamento, já resolvidos pelo pai: o cartão só existe com a expansão Governo */
  debt: NonNullable<EconomyPanel["debt"]>;
};

/** Pontos de dívida a mais pesam em vermelho, a menos em verde. */
const causeTone = (points: number) =>
  Math.abs(points) < 0.0005 ? "text-foreground" : points > 0 ? "text-destructive" : "text-success";

/** A dívida em % do PIB ao longo da partida, com os valores do último fechamento e de onde veio a variação. */
export function DebtCard({ panel, debt }: DebtCardProps) {
  const result = debt.month_result === null ? null : Number(debt.month_result);

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 gap-6 lg:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)] lg:items-center">
          <div className="grid gap-2">
            <div className="flex items-center gap-1.5">
              <h2 className="text-[15px] font-semibold">{DEBT_GDP.label}</h2>
              <InfoHint label="Como ler a dívida">
                <div className="space-y-1 text-left">
                  <p>{DEBT_GDP.definition}</p>
                  <p>{DEBT_GDP.example}</p>
                  <p>{DEBT_GDP.reading}</p>
                </div>
              </InfoHint>
            </div>
            <SeriesChart
              rows={economyRows(panel)}
              dataKey="debt"
              label="Dívida ÷ PIB"
              color="var(--chart-5)"
              reference={{ value: 0.5, label: "50%: o prêmio começa" }}
              height={200}
            />
          </div>

          <div className="grid gap-2.5">
            <p className="text-[13px] leading-normal">
              A dívida do governo, perto de tudo o que o país produz num ano. Acima de 50%, os títulos novos do Tesouro
              passam a cobrar o {RISK_PREMIUM.label.toLowerCase()}: {RISK_PREMIUM.description.toLowerCase()}.
            </p>
            <div className="grid gap-1.5 text-[13px]">
              <div className="flex items-center justify-between gap-4">
                <span>Dívida ÷ PIB</span>
                <span className="font-mono font-semibold">{displayPercent(debt.debt, 1)}</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span>Na história</span>
                <span className="font-mono font-semibold">{displayPercent(debt.history_debt, 1)}</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span className="inline-flex items-center gap-1">
                  {DEBT_RATE.label}
                  <MetricHint metric={DEBT_RATE} />
                </span>
                <span className="font-mono font-semibold">{DEBT_RATE.format(debt.rate)}</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span>Dívida</span>
                <span className="font-mono font-semibold">{displayMoneyLarge(debt.debt_amount)}</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span>PIB em 12 meses</span>
                <span className="font-mono font-semibold">{displayMoneyLarge(debt.gdp)}</span>
              </div>
              {result !== null && (
                <div className="flex items-center justify-between gap-4">
                  <span>Resultado do mês</span>
                  <span className={cn("font-mono font-semibold", result < 0 ? "text-destructive" : "text-success")}>
                    {displayMoneyLarge(result)}
                  </span>
                </div>
              )}
            </div>
            <StabilizingPrimary debt={debt} />
            {debt.causes.months > 0 && <DebtCauses causes={debt.causes} />}
            <Link to="/government?tab=accounts" className="text-[13px] font-medium text-primary hover:underline">
              Ver o orçamento no Governo ›
            </Link>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

type StabilizingPrimaryProps = { debt: NonNullable<EconomyPanel["debt"]> };

/** O primário da partida ao lado do que mantém a dívida parada, com o da história como régua. */
function StabilizingPrimary({ debt }: StabilizingPrimaryProps) {
  const primary = Number(debt.primary);
  const stabilizing = Number(debt.stabilizing_primary);

  return (
    <div className="grid gap-1.5 border-t pt-2.5 text-[13px]">
      <span className="inline-flex items-center gap-1 text-xs font-medium text-muted-foreground">
        {STABILIZING_PRIMARY.label}
        <MetricHint metric={STABILIZING_PRIMARY} />
      </span>
      <div className="flex items-center justify-between gap-4">
        <span>Resultado primário</span>
        <span className="font-mono font-semibold">{STABILIZING_PRIMARY.format(primary)}</span>
      </div>
      <div className="flex items-center justify-between gap-4">
        <span>Estabiliza a dívida</span>
        <span className="font-mono font-semibold">{STABILIZING_PRIMARY.format(stabilizing)}</span>
      </div>
      <div className="flex items-center justify-between gap-4">
        <span>Na história</span>
        <span className="font-mono font-semibold">{STABILIZING_PRIMARY.format(debt.history_stabilizing_primary)}</span>
      </div>
      <p className={cn("font-medium", primary >= stabilizing ? "text-success" : "text-destructive")}>
        {stabilizingNote(primary, stabilizing)}
      </p>
    </div>
  );
}

type DebtCausesProps = { causes: NonNullable<EconomyPanel["debt"]>["causes"] };

/** A variação da dívida ÷ PIB nos últimos meses fechados, aberta nas quatro causas que a somam. */
function DebtCauses({ causes }: DebtCausesProps) {
  const lines = [
    { label: "Juro", points: Number(causes.interest) },
    { label: "Crescimento", points: Number(causes.growth) },
    { label: "Inflação", points: Number(causes.inflation) },
    { label: "Resultado primário", points: Number(causes.primary) },
  ];
  const total = lines.reduce((sum, line) => sum + line.points, 0);

  return (
    <div className="grid gap-1.5 border-t pt-2.5 text-[13px]">
      <span className="inline-flex items-center gap-1 text-xs font-medium text-muted-foreground">
        De onde veio a dívida em {causes.months} {causes.months === 1 ? "mês" : "meses"}, em pontos do PIB
        <MetricHint metric={DEBT_CAUSES} />
      </span>
      {lines.map((line) => (
        <div key={line.label} className="flex items-center justify-between gap-4">
          <span>{line.label}</span>
          <span className={cn("font-mono font-semibold", causeTone(line.points))}>
            {DEBT_CAUSES.format(line.points)}
          </span>
        </div>
      ))}
      <div className="flex items-center justify-between gap-4 border-t pt-1.5">
        <span className="font-medium">= Variação da dívida</span>
        <span className={cn("font-mono font-semibold", causeTone(total))}>{DEBT_CAUSES.format(total)}</span>
      </div>
    </div>
  );
}
