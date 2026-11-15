import { Kpi } from "@/shared/components/kpi";
import { MetricHint } from "@/shared/components/metric-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Progress } from "@/shared/components/ui/progress";
import type { StateCompaniesPanel } from "@/types";
import { BACKLOG, CONTROL_CAP, STATE_STAKE, TREASURY_DIVIDENDS } from "../../lib/government-metrics";
import { capBreakdown, capLabel, capUsage, stakeNote } from "../../lib/state-companies";

type StateCompaniesSummaryProps = { panel: StateCompaniesPanel };

/** A faixa das estatais: o que o governo tem nelas, o que rendem ao Tesouro e o quanto do controle de preço está em uso. */
export function StateCompaniesSummary({ panel }: StateCompaniesSummaryProps) {
  const { summary, companies } = panel;
  const breakdown = capBreakdown(companies);
  const atCap = capUsage(summary) >= 1;

  return (
    <Card>
      <CardContent>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {/* Fatia do governo */}
          <Kpi
            label={
              <>
                {STATE_STAKE.label}
                <MetricHint metric={STATE_STAKE} />
              </>
            }
            value={STATE_STAKE.format(summary.government_value)}
            note={stakeNote(companies)}
          />

          {/* Dividendos ao Tesouro */}
          <Kpi
            label={
              <>
                {TREASURY_DIVIDENDS.label}
                <MetricHint metric={TREASURY_DIVIDENDS} />
              </>
            }
            value={TREASURY_DIVIDENDS.format(summary.treasury_dividends_12m)}
            note="Dividendos dos 12 últimos meses fechados"
            tone="success"
          />

          {/* Inflação represada */}
          <Kpi
            label={
              <>
                {BACKLOG.label}
                <MetricHint metric={BACKLOG} />
              </>
            }
            value={BACKLOG.format(summary.backlog_points)}
            note="Volta ao IPCA quando o controle sair"
            tone={Number(summary.backlog_points) > 0 ? "warning" : "default"}
          />

          {/* Teto do controle */}
          <Kpi
            label={
              <>
                {CONTROL_CAP.label}
                <MetricHint metric={CONTROL_CAP} />
              </>
            }
            value={capLabel(summary.held_points, summary.cap_points)}
            tone={atCap ? "warning" : "default"}
            note={
              <span className="grid gap-1.5">
                <Progress
                  value={capUsage(summary) * 100}
                  size="sm"
                  indicatorTone={atCap ? "warning" : "default"}
                  aria-label="Teto do controle de preço em uso"
                />
                {breakdown || "Nenhuma estatal segura o preço agora"}
              </span>
            }
          />
        </div>
      </CardContent>
    </Card>
  );
}
