import { Flag, TriangleAlert } from "lucide-react";
import { MetricHint, MetricLabel } from "@/shared/components/metric-hint";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Progress } from "@/shared/components/ui/progress";
import { cn } from "@/shared/lib/utils";
import { displayAnnualExpenseMultiple, displayRatePercent } from "@/shared/lib/financial-independence";
import { displayProjectionDistance, type GoalProjection } from "@/shared/lib/goal";
import { GOAL_ETA, INDEPENDENCE_GOAL, RESERVE_MONTHS } from "@/shared/lib/life-metrics";
import { displayMoney, displayMoneyWhole, displayMonthName, displaySignedMoney } from "@/shared/lib/utils/display";
import type { LifeStatus, SimulationData } from "@/types";

// A régua da reserva vai de 0 a 6 meses; a partir daí é "6+"
const RESERVE_FULL_MONTHS = 6;
const RESERVE_FRAGILE_MONTHS = 3;

type LifeCardProps = {
  life: LifeStatus;
  match: SimulationData;
  /** Caixa de hoje, em reais */
  cash: string;
  projection: GoalProjection | null;
};

/** Tom da barra da reserva: crítico abaixo de 3 meses, de atenção até 6 e bom a partir de 6. */
function reserveTone(months: number) {
  if (months >= RESERVE_FULL_MONTHS) return "success";
  if (months >= RESERVE_FRAGILE_MONTHS) return "warning";
  return "destructive";
}

/** "Vida financeira": o mês a mês, a reserva de emergência e a previsão para a meta. */
export function LifeCard({ life, match, cash, projection }: LifeCardProps) {
  const salary = Number(life.monthly_salary);
  const expense = Number(life.monthly_expense);
  const reserveMonths = Number(life.reserve_months);
  const overdraft = Number(life.overdraft_daily_interest) > 0;
  const salaryMissing = life.salary_skipped_by !== null || life.next_salary_skipped_by !== null;
  const leftover = (salaryMissing ? 0 : salary) - expense;
  const startYear = match.start_date.slice(0, 4);

  return (
    <Card>
      <CardHeader className="grid-cols-[1fr_auto]">
        <div className="grid gap-1">
          <CardTitle>Vida financeira</CardTitle>
          <CardDescription>Salário, despesa e reserva desta partida</CardDescription>
        </div>
        <span className="flex items-center gap-1">
          <Badge variant="info">{displayAnnualExpenseMultiple(Number(life.withdrawal_rate))}</Badge>
          <MetricHint metric={INDEPENDENCE_GOAL} />
        </span>
      </CardHeader>

      <CardContent>
        <div className="grid gap-5">
          {/* Caixa no cheque especial */}
          {overdraft && (
            <Alert variant="destructive">
              <TriangleAlert />
              <AlertTitle>Caixa em {displaySignedMoney(cash)} no cheque especial</AlertTitle>
              <AlertDescription>
                Paga uns {displayMoney(life.overdraft_daily_interest)} de juros por pregão (
                {displayRatePercent(life.overdraft_monthly_rate)} ao mês). Venda ou resgate algo para cobrir.
              </AlertDescription>
            </Alert>
          )}

          <div className="grid gap-5 sm:grid-cols-2">
            {/* Todo mês */}
            <div className="grid content-start">
              <span className="mb-1.5 text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
                Todo mês
              </span>
              <MonthRow label="Salário">
                <span
                  className={cn(
                    "font-mono font-semibold",
                    salaryMissing ? "text-muted-foreground line-through" : "text-success",
                  )}
                >
                  +{displayMoney(salary)}
                </span>
              </MonthRow>
              {life.salary_skipped_by && (
                <span className="pb-1.5 text-xs text-destructive">
                  Demitido em {displayMonthName(life.salary_skipped_by)}: o salário de{" "}
                  {displayMonthName(life.salary_skipped_by, 1)} não entrou
                </span>
              )}
              {life.next_salary_skipped_by && (
                <span className="pb-1.5 text-xs text-destructive">
                  Demitido em {displayMonthName(life.next_salary_skipped_by)}: o salário de{" "}
                  {displayMonthName(life.next_salary_skipped_by, 1)} não entra
                </span>
              )}
              <MonthRow label="Despesa">
                <span className="font-mono font-semibold text-destructive">{displaySignedMoney(-expense)}</span>
              </MonthRow>
              <MonthRow label="Sobra para investir">
                <span className={cn("font-mono font-semibold", leftover < 0 && "text-destructive")}>
                  {leftover >= 0 ? "+" : ""}
                  {displaySignedMoney(leftover)}
                </span>
              </MonthRow>
              {!life.inflation_adjusted && (
                <span className="mt-1.5 text-xs text-muted-foreground">
                  Fixos nos reais de {startYear}: esta partida não corrige pelo IPCA.
                </span>
              )}
            </div>

            {/* Reserva de emergência */}
            <div className="grid content-start gap-2">
              <span className="text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
                <MetricLabel metric={RESERVE_MONTHS} />
              </span>
              <span>
                <span className="font-mono text-[22px] font-semibold">{RESERVE_MONTHS.format(reserveMonths)}</span>{" "}
                <span className="text-[13px] text-muted-foreground">de despesa</span>
              </span>
              <div className="grid gap-1">
                <div className="relative">
                  <Progress
                    value={Math.min(reserveMonths / RESERVE_FULL_MONTHS, 1) * 100}
                    size="md"
                    indicatorTone={reserveTone(reserveMonths)}
                    aria-label="Reserva de emergência em meses de despesa"
                  />
                  <span className="absolute -top-0.5 left-1/2 h-3.5 w-px bg-faint-foreground" aria-hidden="true" />
                  <span className="absolute -top-0.5 right-0 h-3.5 w-px bg-faint-foreground" aria-hidden="true" />
                </div>
                <div className="relative flex justify-between font-mono text-[11px] text-muted-foreground">
                  <span>0</span>
                  <span className="absolute left-1/2 -translate-x-1/2">{RESERVE_FRAGILE_MONTHS} meses</span>
                  <span>{RESERVE_FULL_MONTHS}+</span>
                </div>
              </div>
              <span className="text-xs text-muted-foreground">
                {reserveMonths > 0
                  ? `${displayMoneyWhole(cash)} em caixa: cobre a despesa sem precisar vender ação na baixa.`
                  : "Nada em caixa: a próxima despesa cai no cheque especial."}
              </span>
            </div>
          </div>

          {/* Previsão para a meta */}
          {projection && (
            <Alert variant="info">
              <Flag />
              <AlertDescription>
                <span className="flex flex-wrap items-center gap-x-1">
                  No ritmo dos últimos 12 meses, você chega à meta em <b>{projection.monthYear}</b>,{" "}
                  {displayProjectionDistance(projection.months)}.
                  <MetricHint metric={GOAL_ETA} />
                </span>
              </AlertDescription>
            </Alert>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function MonthRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-baseline justify-between gap-3 border-t border-muted py-2">
      <span className="text-[13px] text-muted-foreground">{label}</span>
      <span className="whitespace-nowrap">{children}</span>
    </div>
  );
}
