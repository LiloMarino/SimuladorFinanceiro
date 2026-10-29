import { useState, type ReactNode } from "react";
import { TriangleAlert } from "lucide-react";
import { Kpi } from "@/shared/components/kpi";
import { MetricHint } from "@/shared/components/metric-hint";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { DEBT_GDP, displayPremiumPoints } from "@/shared/lib/budget-metrics";
import { cn } from "@/shared/lib/utils";
import { displayMonthName, displayMoneyLarge, displayPercent, displayDayMonth } from "@/shared/lib/utils/display";
import type { Budget } from "@/types";
import {
  accountBars,
  amountLabel,
  closingDay,
  debtChangeNote,
  debtTone,
  premiumNote,
  resultTone,
  shareLabel,
  type BudgetUnit,
} from "../lib/budget";
import { monthlyLabel, yearShare } from "../lib/base";
import { INTEREST, PRIMARY_RESULT, RESULT, REVENUE } from "../lib/government-metrics";

type BudgetCardProps = { budget: Budget };

/** "março" → "Março", para o título dos botões. */
const capitalize = (text: string) => text.charAt(0).toUpperCase() + text.slice(1);

type SegmentProps = { width: number; className: string; label: string; value: string; children?: ReactNode };

/** Um trecho da barra: o texto só cabe quando o trecho é largo; o rótulo completo vai no title. */
function Segment({ width, className, label, value, children }: SegmentProps) {
  if (width <= 0) return null;
  return (
    <span
      className={cn("flex h-8 items-center justify-center overflow-hidden px-1.5 text-xs font-medium", className)}
      style={{ width: `${width * 100}%` }}
      title={`${label} ${value}`}
    >
      {width >= 0.12 && (children ?? `${label} ${value}`)}
    </span>
  );
}

const HATCH = "bg-[repeating-linear-gradient(135deg,var(--destructive)_0_2px,transparent_2px_8px)]";

/** A conta do mês: duas barras (o que entra e o que sai) e os quatro números que as explicam. */
function ClosedMonth({ budget, unit }: { budget: Budget; unit: BudgetUnit }) {
  const { month, amounts } = budget;
  const bars = accountBars(month);
  const deficit = Math.max(0, -Number(month.result));
  const rate = Number(month.debt) > 0 ? Number(month.interest) / Number(month.debt) : 0;
  const monthName = displayMonthName(month.month_end);
  const debtChange = debtChangeNote(budget.history, month);

  return (
    <>
      <div className="grid grid-cols-[3rem_minmax(0,1fr)] items-center gap-x-3 gap-y-2.5">
        <span className="text-xs font-medium text-muted-foreground">Entra</span>
        <div className="flex overflow-hidden rounded-md">
          <Segment
            width={bars.in.revenue}
            className="bg-success text-white"
            label="Receita"
            value={amountLabel(unit, month.revenue, amounts.revenue)}
          />
          <Segment
            width={bars.in.deficit}
            className={cn(HATCH, "text-destructive")}
            label="Déficit"
            value={amountLabel(unit, deficit, -Number(amounts.result))}
          >
            <b className="rounded-sm bg-card px-1.5 py-px">
              déficit {amountLabel(unit, deficit, -Number(amounts.result))}
            </b>
          </Segment>
        </div>
        <span className="text-xs font-medium text-muted-foreground">Sai</span>
        <div className="flex overflow-hidden rounded-md">
          <Segment
            width={bars.out.spending}
            className="bg-muted-foreground text-white"
            label="Gasto"
            value={amountLabel(unit, month.spending, amounts.spending)}
          />
          <Segment
            width={bars.out.interest}
            className="bg-warning text-white"
            label="Juros"
            value={amountLabel(unit, month.interest, amounts.interest)}
          />
          <Segment
            width={bars.out.surplus}
            className="bg-success-soft text-success"
            label="Sobra"
            value={amountLabel(unit, month.result, amounts.result)}
          />
        </div>
      </div>

      {/* Emendas à base dentro do gasto */}
      {Number(budget.amendments_amount) > 0 && (
        <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
          <Badge variant="info">inclui {yearShare(budget.amendments_ratio)} de emendas à base</Badge>
          {budget.amendments.map((line) => `${line.abbr} ${monthlyLabel(line.amount)}`).join(" + ")} em {monthName}. A
          emenda é gasto como outro qualquer: soma ao déficit e vira dívida.
        </div>
      )}

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {/* Primário */}
        <Kpi
          label={
            <>
              {PRIMARY_RESULT.label}
              <MetricHint metric={PRIMARY_RESULT} />
            </>
          }
          value={amountLabel(unit, month.primary, amounts.primary)}
          note="Receita menos gasto. As medidas mexem aqui."
          tone={resultTone(month.primary)}
        />

        {/* Dívida */}
        <Kpi
          label={
            <>
              {DEBT_GDP.label}
              <MetricHint metric={DEBT_GDP} />
            </>
          }
          value={DEBT_GDP.format(month.debt)}
          note={
            <>
              {displayMoneyLarge(amounts.debt)}. {premiumNote(month, budget.premium_floor)}
              {debtChange && <span className="block">{debtChange}</span>}
            </>
          }
          tone={debtTone(month)}
        />

        {/* Juros */}
        <Kpi
          label={
            <>
              {INTEREST.label}
              <MetricHint metric={INTEREST} />
            </>
          }
          value={amountLabel(unit, -Number(month.interest), -Number(amounts.interest))}
          note={`${shareLabel(month.debt)} do PIB × juro de ${displayPercent(rate, 2)} (SELIC mais o prêmio).`}
          tone="warning"
        />

        {/* Resultado */}
        <Kpi
          label={
            <>
              {RESULT.label} de {monthName}
              <MetricHint metric={RESULT} />
            </>
          }
          value={amountLabel(unit, month.result, amounts.result)}
          note={`${displayMoneyLarge(amounts.result)} em ${monthName}. ${
            Number(month.result) < 0 ? "O déficit vira dívida." : "A sobra abate a dívida."
          }`}
          tone={resultTone(month.result)}
        />
      </div>
    </>
  );
}

/** Antes do primeiro fechamento: a receita por ano, o dia em que o resultado sai e a dívida da conta inicial. */
function FirstMonth({ budget }: { budget: Budget }) {
  const { month } = budget;
  const closes = closingDay(budget.today);
  const monthName = displayMonthName(closes);

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <Kpi
        label={
          <>
            {REVENUE.label}
            <MetricHint metric={REVENUE} />
          </>
        }
        value={shareLabel(month.revenue)}
        note="do PIB por ano"
      />
      <Kpi label="Gasto" value={shareLabel(month.spending)} note="do PIB por ano" />
      <Kpi
        label={
          <>
            {RESULT.label} de {monthName}
            <MetricHint metric={RESULT} />
          </>
        }
        value="—"
        note={`sai em ${displayDayMonth(closes)}, no primeiro fechamento`}
      />
      <Kpi
        label={
          <>
            {DEBT_GDP.label}
            <MetricHint metric={DEBT_GDP} />
          </>
        }
        value={DEBT_GDP.format(month.debt)}
        note={`${premiumNote(month, budget.premium_floor)} · a da conta inicial`}
        tone={debtTone(month)}
      />
    </div>
  );
}

/** "A conta do país": o mês fechado em R$ ou em % do PIB por ano, com o alerta quando a dívida passa do PIB. */
export function BudgetCard({ budget }: BudgetCardProps) {
  const [unit, setUnit] = useState<BudgetUnit>("year");
  const { month } = budget;
  const monthName = capitalize(displayMonthName(month.closed ? month.month_end : closingDay(budget.today)));

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 gap-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="grid gap-1">
              <div className="flex items-center gap-2">
                <h2 className="text-[15px] font-semibold">A conta do país</h2>
                <Badge variant="secondary" size="sm">
                  a sala vê
                </Badge>
              </div>
              <span className="text-[13px] text-muted-foreground">
                O que entra e o que sai do governo, em % do PIB por ano. A barra de cima é o que entra; a de baixo, o
                que sai: gasto mais juros.
              </span>
            </div>
            {month.closed && (
              <ToggleGroup
                variant="segmented"
                aria-label="Unidade da conta"
                value={[unit]}
                onValueChange={(values) => values[0] && setUnit(values[0] as BudgetUnit)}
              >
                <ToggleGroupItem value="month">{monthName}, em R$</ToggleGroupItem>
                <ToggleGroupItem value="year">Por ano, em % do PIB</ToggleGroupItem>
              </ToggleGroup>
            )}
          </div>

          {/* Dívida acima de todo o PIB */}
          {Number(month.debt) > 1 && (
            <Alert variant="destructive">
              <TriangleAlert />
              <AlertTitle>A dívida passou de 100% do PIB.</AlertTitle>
              <AlertDescription>
                Cada ponto a mais pesa mais no prêmio: hoje, {displayPremiumPoints(month.premium)}. Os juros custam{" "}
                {shareLabel(month.interest)} do PIB por ano.
              </AlertDescription>
            </Alert>
          )}

          {month.closed ? <ClosedMonth budget={budget} unit={unit} /> : <FirstMonth budget={budget} />}
        </div>
      </CardContent>
    </Card>
  );
}
