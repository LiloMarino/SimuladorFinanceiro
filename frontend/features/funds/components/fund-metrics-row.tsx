import { Kpi } from "@/shared/components/kpi";
import { MetricHint, MetricLabel } from "@/shared/components/metric-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import {
  displayMoney,
  displayMoneyWhole,
  displayPercent,
  displayPercentagePoints,
  displaySignedPercent,
} from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { premium } from "../lib/fund-math";
import {
  MANAGEMENT_FEE,
  MARKET_PRICE,
  NAV_PER_QUOTA,
  NET_WORTH,
  PERFORMANCE_FEE,
  PREMIUM,
  RETURN_VS_CDI,
} from "../lib/fund-metrics";
import { netWorthOf } from "../lib/fund-view";

const EMPTY = "—";

/** O ágio de hoje em conta: preço no mercado sobre patrimônio por cota. */
function PremiumToday({ price, nav }: { price: number; nav: number }) {
  return (
    <p>
      Hoje: {displayMoney(price)} ÷ {displayMoney(nav)} − 1 = {displaySignedPercent(premium(price, nav), 1)}.
    </p>
  );
}

/** Os quatro números que valem para quem gere e para quem olha: patrimônio, patrimônio por cota, preço e ágio. */
function CommonKpis({ fund }: { fund: FundDetails }) {
  const nav = fund.nav === null ? null : Number(fund.nav);
  const price = fund.price === null ? null : Number(fund.price);
  const hasPremium = nav !== null && price !== null;

  return (
    <>
      <Kpi
        label={<MetricLabel metric={NET_WORTH} />}
        value={displayMoneyWhole(netWorthOf(fund))}
        note={NET_WORTH.description}
      />
      <Kpi
        label={<MetricLabel metric={NAV_PER_QUOTA} />}
        value={nav === null ? EMPTY : displayMoney(nav)}
        note={NAV_PER_QUOTA.description}
      />
      <Kpi
        label={<MetricLabel metric={MARKET_PRICE} />}
        value={price === null ? EMPTY : displayMoney(price)}
        note={price === null ? "Ainda sem negócio no mercado" : MARKET_PRICE.description}
      />
      <Kpi
        label={
          <MetricLabel metric={PREMIUM} extra={hasPremium ? <PremiumToday price={price} nav={nav} /> : undefined} />
        }
        value={hasPremium ? displaySignedPercent(premium(price, nav), 1) : EMPTY}
        note={PREMIUM.description}
      />
    </>
  );
}

/** A rentabilidade em 12 meses contra o CDI, com a diferença em pontos percentuais. */
function ReturnKpi({ fund }: { fund: FundDetails }) {
  const gain = fund.return_12m === null ? null : Number(fund.return_12m);
  const cdi = fund.cdi_12m === null ? null : Number(fund.cdi_12m);
  const beats = gain !== null && cdi !== null ? gain >= cdi : null;

  return (
    <Kpi
      label={<MetricLabel metric={RETURN_VS_CDI} />}
      value={gain === null ? EMPTY : displaySignedPercent(gain, 1)}
      tone={beats === null ? "default" : beats ? "success" : "destructive"}
      note={
        gain !== null && cdi !== null
          ? `CDI ${displayPercent(cdi, 1)} · ${displayPercentagePoints(gain - cdi, 1)} sobre o CDI`
          : RETURN_VS_CDI.description
      }
    />
  );
}

/** As taxas do gestor, como a sala as vê: administração ao ano e performance sobre o que passa do CDI. */
function FeesKpi({ fund }: { fund: FundDetails }) {
  return (
    <Kpi
      label={
        <span className="inline-flex items-center gap-1">
          Taxas do gestor
          <MetricHint metric={MANAGEMENT_FEE} />
          <MetricHint metric={PERFORMANCE_FEE} />
        </span>
      }
      value={`${displayPercent(fund.management_fee, 1, { trim: true })} · ${displayPercent(fund.performance_fee, 1, { trim: true })}`}
      note="Administração ao ano · performance sobre o que passa do CDI"
    />
  );
}

/** Os cinco números do topo: o gestor vê a rentabilidade contra o CDI, quem olha vê as taxas do gestor. */
export function FundMetricsRow({ fund, viewer }: { fund: FundDetails; viewer: boolean }) {
  return (
    <Card>
      <CardContent>
        <div className="grid grid-cols-2 gap-x-6 gap-y-5 md:grid-cols-3 xl:grid-cols-5">
          <CommonKpis fund={fund} />
          {viewer ? <FeesKpi fund={fund} /> : <ReturnKpi fund={fund} />}
        </div>
      </CardContent>
    </Card>
  );
}
