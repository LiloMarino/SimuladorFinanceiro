import { useState } from "react";
import { Info, Users } from "lucide-react";
import { MetricHint } from "@/shared/components/metric-hint";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth, displayMonthShort } from "@/shared/lib/utils/display";
import type { GovernmentPanel } from "@/types";
import {
  ALL_GROUPS,
  TREND_LABEL,
  TREND_VARIANT,
  closingSentence,
  deltaLabel,
  neutralGovernmentSentence,
  selectedSeries,
  selectionLabel,
  trendOf,
  verdictOf,
} from "../lib/approval";
import type { Selection } from "../lib/approval";
import { approvalTone, signedPoints } from "../lib/government";
import { APPROVAL } from "../lib/government-metrics";
import { ApprovalChart } from "./approval-chart";
import { ApprovalGroups } from "./approval-groups";
import { ApprovalReasons } from "./approval-reasons";
import { ImpeachmentFloor } from "./impeachment-floor";

const TONES = { success: "text-success", warning: "text-warning", destructive: "text-destructive" } as const;
const VERDICT_TONES = { APPROVES: "text-success", NEUTRAL: "text-foreground", REPROVES: "text-destructive" } as const;

type ApprovalCardProps = { panel: GovernmentPanel };

/** A aprovação do governo: o número de hoje, a satisfação de cada grupo de eleitores, o alvo de cada um e o piso do impeachment. */
export function ApprovalCard({ panel }: ApprovalCardProps) {
  const [selection, setSelection] = useState<Selection>(ALL_GROUPS);
  const approval = panel.approval;

  if (!approval) {
    return (
      <Card>
        <CardContent>
          <div className="grid content-start gap-2.5">
            <h2 className="text-[15px] font-semibold">Aprovação</h2>
            <Alert variant="muted">
              <Users />
              <AlertTitle>Governo neutro do computador</AlertTitle>
              <AlertDescription>{neutralGovernmentSentence(panel)}</AlertDescription>
            </Alert>
          </div>
        </CardContent>
      </Card>
    );
  }

  const series = selectedSeries(approval, selection);
  const group = approval.groups.find((item) => item.group === selection);
  const atInauguration = approval.history.length <= 1;
  const tone = group ? VERDICT_TONES[verdictOf(series.value, approval)] : TONES[approvalTone(approval)];
  const trend = trendOf(series.value, series.target);
  const delta = deltaLabel(series.value, series.previous);
  const closedMonth = approval.history.at(-1)?.date ?? approval.closes_on;
  const president = panel.term?.president?.name ?? null;
  const subject = group ? selectionLabel(selection).toLowerCase() : "eleitores";

  return (
    <Card id="approval">
      <CardContent>
        <div className="grid min-w-0 content-start gap-3.5">
          <div className="flex items-center justify-between gap-3">
            <h2 className="flex items-center gap-1.5 text-[15px] font-semibold">
              Aprovação{group && ` · ${subject}`}
              <MetricHint metric={APPROVAL} />
            </h2>
            <span className="text-xs text-muted-foreground">o mês fecha em {displayDayMonth(approval.closes_on)}</span>
          </div>

          <div className="flex items-end gap-4">
            <span className={cn("font-mono text-4xl leading-tight font-semibold tabular-nums", tone)}>
              {series.value}%
            </span>
            {!atInauguration && (
              <div className="flex items-center gap-1.5 pb-1.5 text-[13px]">
                {delta && (
                  <>
                    <span
                      className={cn(
                        "font-mono text-xs",
                        series.value > (series.previous ?? 0) ? "text-success" : "text-destructive",
                      )}
                    >
                      {delta}
                    </span>
                    <span className="text-muted-foreground">em {displayMonthShort(closedMonth)}</span>
                  </>
                )}
                <Badge variant={TREND_VARIANT[trend]} size="sm">
                  alvo {series.target}%: {TREND_LABEL[trend]}
                </Badge>
              </div>
            )}
          </div>

          <p className="text-xs leading-normal text-muted-foreground">
            {group
              ? `De cada 100 ${subject}, ${series.value} aprovam o governo. A aprovação geral (${approval.value}%) é a média dos 6 grupos pelo tamanho de cada um e é a chance de cada medida passar no Congresso.`
              : atInauguration
                ? `Posse em ${displayDayMonth(closedMonth)}: cada grupo começa satisfeito na proporção em que votou em ${president ?? "quem governa"} no 2º turno. O alvo de cada grupo sai no fechamento de ${displayDayMonth(approval.closes_on)}.`
                : `De cada 100 eleitores, ${approval.value} aprovam o governo. É a média dos 6 grupos pelo tamanho de cada um e a chance de cada medida passar no Congresso.`}
          </p>

          <ApprovalChart approval={approval} selection={selection} />

          {/* Grupos de eleitores */}
          <div className="grid gap-2">
            <span className="text-[13px] font-semibold">Por grupo</span>
            <span className="-mt-1 text-xs leading-normal text-muted-foreground">
              Clique num grupo para ver a aprovação dele no gráfico; Geral volta ao total.
            </span>
            <ApprovalGroups approval={approval} selection={selection} onSelect={setSelection} president={president} />
            {group && !atInauguration && <ApprovalReasons group={group} approval={approval} />}
            <div className="flex flex-wrap gap-x-3.5 gap-y-1 text-[11.5px] text-muted-foreground">
              <span className="inline-flex items-center gap-1.5">
                <span className="h-2 w-4 rounded-xs bg-border" />
                faixa neutra, {approval.reproves_below} a {approval.approves_above}
              </span>
              <span className="inline-flex items-center gap-1.5">
                <span className="h-3 w-0.5 bg-foreground" />
                alvo: onde a satisfação para se nada mudar
              </span>
            </div>
          </div>

          {/* Medidas aprovadas que ainda vão pesar no alvo */}
          {approval.upcoming.length > 0 && (
            <ul className="grid">
              {approval.upcoming.map((effect) => (
                <li
                  key={effect.measure_id}
                  className="flex items-center gap-2.5 border-t py-1.75 text-xs text-muted-foreground"
                >
                  <span className="min-w-11 shrink-0 font-mono font-semibold whitespace-nowrap">
                    {signedPoints(effect.impact)}
                  </span>
                  <span className="flex-1">{effect.description}</span>
                </li>
              ))}
            </ul>
          )}

          {/* O que o fechamento fez com o partido do presidente, só para os filiados */}
          {approval.closing && (
            <Alert variant="info">
              <Info />
              <AlertTitle>
                No fechamento de {displayDayMonth(approval.closing.month)}, para o {approval.closing.party_abbr}
              </AlertTitle>
              <AlertDescription>{closingSentence(approval.closing.party_abbr, approval.closing)}</AlertDescription>
            </Alert>
          )}

          <ImpeachmentFloor panel={panel} />
        </div>
      </CardContent>
    </Card>
  );
}
