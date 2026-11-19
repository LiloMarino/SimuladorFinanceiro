import { Card, CardContent } from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import { FundSection } from "@/shared/components/fund-section";
import { Kpi } from "@/shared/components/kpi";
import { MetricLabel } from "@/shared/components/metric-hint";
import { ReturnKpi, TotalReturnKpi } from "@/shared/components/fund-metrics-row";
import { StackedBar } from "@/shared/components/stacked-bar";
import { DIVIDEND_YIELD } from "@/shared/lib/fund-metrics";
import { fundStage } from "@/shared/lib/fund-view";
import { cn } from "@/shared/lib/utils";
import { displayMoney, displayMonthName, displayPercent } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { HOLDING_CLASSES } from "../../lib/fund-classes";
import type { FundTabActions } from "../../lib/fund-tabs";
import { fundYield } from "../../lib/fund-yield";
import { FundPriceChart } from "../fund-price-chart";

type OverviewTabProps = { fund: FundDetails; actions: Pick<FundTabActions, "goTo"> };

/** A gestora que ainda não abriu: sem mercado, o que há para ver são os passos de Suas ações. */
function ClosedOverview({ onSteps }: { onSteps: () => void }) {
  return (
    <Card>
      <CardContent>
        <div className="mx-auto grid max-w-lg justify-items-center gap-3 py-10 text-center">
          <h2 className="text-[17px] font-semibold">Preço e histórico chegam com o mercado</h2>
          <p className="text-[13px] text-muted-foreground">
            Enquanto a gestora está fechada, só o gestor tem cotas e elas não são negociadas. Não há preço no mercado,
            rendimento pago nem retorno para mostrar.
          </p>
          <p className="text-[13px] text-muted-foreground">
            Eles aparecem depois que a oferta pública fecha e a cota passa a ser negociada.
          </p>
          <Button variant="fund" onClick={onSteps}>
            Ver os passos em Suas ações
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

/** O card "Quanto rendeu": rentabilidade, retorno total e dividend yield. */
function ReturnsCard({ fund }: { fund: FundDetails }) {
  const result = fundYield(fund);

  return (
    <FundSection title="Quanto rendeu">
      <div className="grid gap-4">
        <ReturnKpi fund={fund} />
        <TotalReturnKpi fund={fund} />
        <Kpi
          label={<MetricLabel metric={DIVIDEND_YIELD} />}
          value={result.rate === null ? "—" : displayPercent(result.rate, 1)}
          note={
            result.rate === null
              ? "Ainda sem rendimento pago"
              : `${displayMoney(result.perQuota)} pagos por cota em 12 meses ÷ ${displayMoney(result.base)} de preço`
          }
        />
      </div>
    </FundSection>
  );
}

/** O card "Agora na gestora": o que está em andamento e para onde ir ver. */
function NowCard({ fund, actions }: { fund: FundDetails; actions: Pick<FundTabActions, "goTo"> }) {
  const plan = fund.distribution;
  const voting = fund.assembly.current?.status === "VOTING";

  return (
    <FundSection title="Agora na gestora">
      <div className="grid">
        <div className="flex items-center gap-3 border-t border-muted py-2.5 first:border-t-0 first:pt-0">
          <div className="grid min-w-0 flex-1 gap-0.5">
            <b className="text-[13px] font-semibold">Rendimento de {displayMonthName(plan.data_com_on)}</b>
            <span className="text-xs text-muted-foreground">
              {displayMoney(plan.projected_per_quota)} por cota, se fechasse hoje
            </span>
          </div>
          <Button size="xs" variant="outline" onClick={() => actions.goTo("income")}>
            Rendimentos
          </Button>
        </div>
        {voting && (
          <div className="flex items-center gap-3 border-t border-muted py-2.5">
            <div className="grid min-w-0 flex-1 gap-0.5">
              <b className="text-[13px] font-semibold">Votação aberta</b>
              <span className="text-xs text-muted-foreground">Os cotistas decidem quem gere a gestora</span>
            </div>
            <Button size="xs" variant="outline" onClick={() => actions.goTo("assembly")}>
              Assembleia
            </Button>
          </div>
        )}
      </div>
    </FundSection>
  );
}

/** O card "Composição": a barra do patrimônio por classe e as dívidas que saem dele. */
function CompositionCard({ fund, actions }: { fund: FundDetails; actions: Pick<FundTabActions, "goTo"> }) {
  const debts = Number(fund.fees.loan_debt) + Number(fund.fees.payable);

  return (
    <FundSection title="Composição">
      <div className="grid gap-3">
        <StackedBar
          size="lg"
          segments={fund.composition.map((item) => ({
            key: item.asset_class,
            fraction: Number(item.fraction),
            color: HOLDING_CLASSES[item.asset_class].color,
          }))}
        />
        <ul className="grid gap-1.5">
          {fund.composition.map((item) => (
            <li key={item.asset_class} className="flex items-center gap-2 text-[13px]">
              <span className={cn("size-2.5 rounded-full", HOLDING_CLASSES[item.asset_class].color)} />
              <span className="flex-1">{HOLDING_CLASSES[item.asset_class].label}</span>
              <span className="font-mono text-muted-foreground">{displayMoney(item.value)}</span>
              <span className="w-14 text-right font-mono font-semibold">{displayPercent(item.fraction, 1)}</span>
            </li>
          ))}
        </ul>
        {debts > 0 && (
          <p className="text-xs text-muted-foreground">
            Dívidas de {displayMoney(debts)} (empréstimo e taxa a pagar) saem do patrimônio.
          </p>
        )}
        <Button size="xs" variant="link-fund" className="justify-self-start" onClick={() => actions.goTo("report")}>
          Ver no Relatório
        </Button>
      </div>
    </FundSection>
  );
}

/** A visão geral: preço da cota, retorno, o que está em andamento e a composição da carteira. */
export function OverviewTab({ fund, actions }: OverviewTabProps) {
  if (fundStage(fund) === "closed") {
    return (
      <div className="pt-3">
        <ClosedOverview onSteps={() => actions.goTo("actions")} />
      </div>
    );
  }

  return (
    <div className="grid items-start gap-5 pt-3 xl:grid-cols-[minmax(0,1fr)_360px]">
      <FundPriceChart fund={fund} />
      <div className="grid gap-5">
        <ReturnsCard fund={fund} />
        <NowCard fund={fund} actions={actions} />
      </div>
      <div className="xl:col-span-2">
        <CompositionCard fund={fund} actions={actions} />
      </div>
    </div>
  );
}
