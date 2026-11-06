import { useState } from "react";
import { Kpi } from "@/shared/components/kpi";
import { MarkedSlider } from "@/shared/components/marked-slider";
import { MetricHint } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { displayPremiumPoints } from "@/shared/lib/budget-metrics";
import { displayDayMonth, displayPercent } from "@/shared/lib/utils/display";
import type { GovernmentMonetary } from "@/types";
import { useSetSelic } from "../hooks/mutations/useSetSelic";
import { daysUntil } from "../lib/government";
import { COPOM_SELIC, CREDIBILITY, MEETING_CAP, POLICY_REAL_RATE } from "../lib/government-metrics";
import { credibilityTone, moveLabel, realRateReading, realRateTone, selicWindow, toPoints } from "../lib/monetary";

type SelicCardProps = {
  monetary: GovernmentMonetary;
  today: string;
  isPresident: boolean;
};

/** A SELIC nas mãos do governo: a taxa e o juro real de hoje, a próxima reunião do Copom e a credibilidade; o presidente marca a decisão. */
export function SelicCard({ monetary, today, isPresident }: SelicCardProps) {
  const days = daysUntil(today, monetary.next_meeting);
  const plan = monetary.plan;

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-3.5">
          {/* Cabeçalho */}
          <div className="grid gap-1">
            <span className="text-xs font-semibold tracking-[.06em] text-faint-foreground uppercase">Juros</span>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-[15px] font-semibold">SELIC no Copom</h2>
              {plan !== null && <Badge variant="info">decisão marcada: {displayPercent(plan)}</Badge>}
            </div>
            <span className="text-[13px] text-muted-foreground">
              {monetary.by_government
                ? "O presidente decide a SELIC nas reuniões do Copom. A decisão é marcada antes e vale do dia seguinte à reunião; sem decisão, a SELIC fica."
                : "Até o primeiro presidente de jogador tomar posse, o Banco Central decide a SELIC como na história."}
            </span>
          </div>

          {/* Números de hoje */}
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <Kpi
              label={
                <>
                  {COPOM_SELIC.label}
                  <MetricHint metric={COPOM_SELIC} />
                </>
              }
              value={COPOM_SELIC.format(monetary.selic)}
              note={`IPCA de 12 meses em ${displayPercent(monetary.ipca)}, meta de ${displayPercent(monetary.target, 1)}.`}
            />
            <Kpi
              label={
                <>
                  {POLICY_REAL_RATE.label}
                  <MetricHint metric={POLICY_REAL_RATE} />
                </>
              }
              value={POLICY_REAL_RATE.format(monetary.real_rate)}
              tone={realRateTone(monetary.real_rate)}
              note={`Neutro em ${displayPercent(monetary.neutral_real_rate, 0)}. ${realRateReading(monetary.real_rate)}`}
            />
            <Kpi
              label={
                <>
                  Próxima reunião
                  <MetricHint metric={MEETING_CAP} />
                </>
              }
              value={displayDayMonth(monetary.next_meeting)}
              note={`${days === 0 ? "Hoje" : `Faltam ${days} ${days === 1 ? "dia" : "dias"}`}. Anda até ${MEETING_CAP.format(monetary.cap)}.`}
            />
            <Kpi
              label={
                <>
                  {CREDIBILITY.label}
                  <MetricHint metric={CREDIBILITY} />
                </>
              }
              value={CREDIBILITY.format(monetary.credibility)}
              tone={credibilityTone(monetary.credibility)}
              note={
                Number(monetary.credibility_premium) > 0
                  ? `A dívida paga ${displayPremiumPoints(monetary.credibility_premium)} de prêmio a mais.`
                  : "Sem custo no prêmio de risco da dívida."
              }
            />
          </div>

          {/* Decisão da próxima reunião */}
          {isPresident && monetary.by_government && (
            <SelicPlanner key={`${plan}-${monetary.selic}-${monetary.cap}`} monetary={monetary} />
          )}
        </div>
      </CardContent>
    </Card>
  );
}

/** O controle da decisão: a SELIC dentro da janela que a reunião alcança, marcada para a próxima reunião. */
function SelicPlanner({ monetary }: { monetary: GovernmentMonetary }) {
  const range = selicWindow(monetary);
  const marked = monetary.plan === null ? null : toPoints(monetary.plan);
  const [planned, setPlanned] = useState(marked ?? range.nearest);
  const setSelic = useSetSelic();
  const unchanged = planned === marked;

  return (
    <div className="grid gap-3 rounded-lg border bg-subtle p-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <span className="text-sm font-medium">Decisão para a reunião de {displayDayMonth(monetary.next_meeting)}</span>
        <span className="font-mono text-sm font-semibold">
          {displayPercent(planned / 100)}{" "}
          <span className="font-normal text-muted-foreground">({moveLabel(planned, range.selic)})</span>
        </span>
      </div>
      <MarkedSlider
        aria-label="SELIC da próxima reunião"
        value={planned}
        onValueChange={setPlanned}
        min={range.min}
        max={range.max}
        step={range.step}
        marks={[
          // Com a SELIC em zero, a ponta de baixo é a própria taxa de hoje
          ...(range.min < range.selic ? [{ value: range.min, label: displayPercent(range.min / 100) }] : []),
          { value: range.selic, label: "hoje" },
          { value: range.max, label: displayPercent(range.max / 100) },
        ]}
      />
      <div className="flex flex-wrap items-center justify-end gap-2">
        {marked !== null && (
          <Button
            variant="outline"
            size="sm"
            disabled={setSelic.isPending}
            onClick={() => setSelic.mutate({ selic: null })}
          >
            Desmarcar
          </Button>
        )}
        <Button
          size="sm"
          disabled={unchanged || setSelic.isPending}
          onClick={() => setSelic.mutate({ selic: (planned / 100).toFixed(4) })}
        >
          {marked === null ? "Marcar decisão" : "Trocar decisão"}
        </Button>
      </div>
    </div>
  );
}
