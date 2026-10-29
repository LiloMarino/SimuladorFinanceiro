import { Info } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { MetricLabel } from "@/shared/components/metric-hint";
import { Popover, PopoverContent, PopoverTrigger } from "@/shared/components/ui/popover";
import { Progress } from "@/shared/components/ui/progress";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { GovernmentMeasure, GovernmentPanel } from "@/types";
import { useReproposeMeasure } from "../hooks/mutations/useReproposeMeasure";
import { useWithdrawMeasure } from "../hooks/mutations/useWithdrawMeasure";
import { useToday } from "../hooks/useToday";
import { signedShareLabel, shareLabel } from "../lib/budget";
import { daysUntil, nextStep, STAGES } from "../lib/government";
import { inflationTone, signedIpca } from "@/shared/lib/effects";
import { isSpending } from "@/shared/lib/spending-kinds";
import { CHANCE, QUEUE_BUDGET, QUEUE_INFLATION } from "../lib/government-metrics";
import { MeasureSteps } from "./measure-steps";

type QueueCardProps = { panel: GovernmentPanel };

/** A fila pública do Congresso: o que o presidente propôs, o que espera para valer e o que caiu. */
export function QueueCard({ panel }: QueueCardProps) {
  const today = useToday(panel);
  const withdraw = useWithdrawMeasure();
  const repropose = useReproposeMeasure();
  // O IPCA que a fila inteira soma no pico: só as medidas de gasto que ainda podem valer
  const queueInflation = panel.queue
    .filter((measure) => measure.status === "QUEUED" || measure.status === "APPROVED")
    .reduce((sum, measure) => sum + Number(measure.inflation_effect), 0);

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-3.5">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-[15px] font-semibold">Medidas a caminho</h2>
            <Badge variant="secondary">Próxima votação: {displayDayMonth(panel.next_vote)}</Badge>
          </div>

          {panel.queue.length === 0 ? (
            <Empty>
              <EmptyHeader>
                <EmptyTitle>Nenhuma medida a caminho</EmptyTitle>
                <EmptyDescription>
                  {panel.is_president
                    ? "Proponha uma mudança de imposto ou de gasto: ela entra na fila e o Congresso vota no fechamento do mês."
                    : "Quando o presidente propuser uma mudança de imposto ou de gasto, ela aparece aqui para a sala toda."}
                </EmptyDescription>
              </EmptyHeader>
            </Empty>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Etapa</TableHead>
                  <TableHead>Medida</TableHead>
                  <TableHead numeric>
                    <MetricLabel metric={QUEUE_BUDGET} />
                  </TableHead>
                  <TableHead numeric variant="tinted">
                    <MetricLabel metric={QUEUE_INFLATION} />
                  </TableHead>
                  <TableHead>Próximo passo</TableHead>
                  <TableHead numeric>
                    <span className="inline-flex items-center gap-1">
                      {CHANCE.label}
                      <Popover>
                        <PopoverTrigger type="button" aria-label="Como uma medida vira regra">
                          <Info className="size-4 text-muted-foreground" />
                        </PopoverTrigger>
                        <PopoverContent side="top" className="w-auto">
                          <MeasureSteps panel={panel} />
                        </PopoverContent>
                      </Popover>
                    </span>
                  </TableHead>
                  <TableHead />
                </TableRow>
              </TableHeader>
              <TableBody>
                {panel.queue.map((measure) => (
                  <TableRow key={measure.id}>
                    <TableCell>
                      <Badge variant={STAGES[measure.status].variant} size="sm">
                        {STAGES[measure.status].label}
                      </Badge>
                    </TableCell>
                    <TableCell className="whitespace-normal">
                      <span className="grid gap-0.5">
                        <span className="flex flex-wrap items-center gap-1.5">
                          <b className="font-medium">{measure.title}</b>
                          {measure.fulfills_promise && (
                            <Badge variant="info" size="sm">
                              cumpre a promessa
                            </Badge>
                          )}
                        </span>
                        <span className="text-xs text-muted-foreground">{stageDate(measure)}</span>
                      </span>
                    </TableCell>
                    <TableCell numeric>
                      <span className={budgetTone(measure.budget_effect)}>
                        {signedShareLabel(measure.budget_effect)}
                      </span>
                    </TableCell>
                    <TableCell numeric tinted>
                      {isSpending(measure.kind) ? (
                        <span
                          className={
                            measure.status === "QUEUED" || measure.status === "APPROVED"
                              ? INFLATION_TONE[inflationTone(measure.inflation_effect)]
                              : INFLATION_TONE.default
                          }
                        >
                          {signedIpca(measure.inflation_effect)}
                        </span>
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </TableCell>
                    <TableCell className="whitespace-normal">{nextStep(measure, today)}</TableCell>
                    <TableCell numeric>
                      <ChanceCell measure={measure} today={today} vigenceDays={panel.vigence_days} />
                    </TableCell>
                    <TableCell numeric>
                      {measure.can_withdraw && (
                        <Button
                          size="xs"
                          variant="outline"
                          disabled={withdraw.isPending}
                          onClick={() => withdraw.mutate(measure.id)}
                        >
                          Retirar
                        </Button>
                      )}
                      {measure.can_repropose && (
                        <Button
                          size="xs"
                          variant="outline"
                          disabled={repropose.isPending}
                          onClick={() => repropose.mutate(measure.id)}
                        >
                          Propor de novo
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
                <TableRow>
                  <TableCell colSpan={2}>
                    <b>Se a fila inteira passar</b>
                  </TableCell>
                  <TableCell numeric>
                    <b className={budgetTone(panel.queue_budget.total)}>{signedShareLabel(panel.queue_budget.total)}</b>
                  </TableCell>
                  <TableCell numeric tinted>
                    <b className={INFLATION_TONE[inflationTone(queueInflation)]}>{signedIpca(queueInflation)}</b>
                  </TableCell>
                  <TableCell colSpan={3} variant="note" className="whitespace-normal">
                    resultado de {shareLabel(panel.queue_budget.result_now)} para{" "}
                    {shareLabel(panel.queue_budget.result_if_passes)} do PIB por ano
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          )}

          <p className="rounded-lg bg-subtle px-2.5 py-2 text-xs leading-normal text-muted-foreground">
            No fechamento de cada mês, o Congresso vota a fila inteira. Cada medida passa com chance igual à aprovação
            do governo naquele dia; aprovada, espera {panel.vigence_days} dias para valer.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

const INFLATION_TONE = { destructive: "text-destructive", success: "text-success", default: "text-muted-foreground" };

/** Medida que melhora o resultado do governo pesa em verde; a que piora, em vermelho. */
function budgetTone(change: string | number) {
  const value = Number(change);
  if (value > 0) return "text-success";
  return value < 0 ? "text-destructive" : "text-muted-foreground";
}

/** "Proposta em 02 mar", "Aprovada em 29 fev": o dia em que a etapa atual começou. */
function stageDate(measure: GovernmentMeasure) {
  switch (measure.status) {
    case "QUEUED":
      return `Proposta em ${displayDayMonth(measure.proposed)}`;
    case "APPROVED":
      return measure.vote_date ? `Aprovada em ${displayDayMonth(measure.vote_date)}` : "Aprovada";
    case "REJECTED":
      return measure.vote_date ? `Rejeitada em ${displayDayMonth(measure.vote_date)}` : "Rejeitada";
    default:
      return "";
  }
}

type ChanceCellProps = { measure: GovernmentMeasure; today: string; vigenceDays: number };

/** Na fila, a chance de passar hoje; aprovada, o quanto da espera já correu. */
function ChanceCell({ measure, today, vigenceDays }: ChanceCellProps) {
  if (measure.status === "QUEUED" && measure.chance !== null) return <span>{measure.chance}%</span>;
  if (measure.status !== "APPROVED" || !measure.effective) return null;
  const waited = vigenceDays - daysUntil(today, measure.effective);
  return (
    <span className="grid min-w-30 gap-0.75">
      <Progress value={(waited / vigenceDays) * 100} size="sm" aria-label="Dias de espera" />
      <span className="text-[11px] text-muted-foreground">
        {waited} de {vigenceDays} dias
      </span>
    </span>
  );
}
