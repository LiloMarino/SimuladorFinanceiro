import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { MetricLabel } from "@/shared/components/metric-hint";
import { CHART_TICK } from "@/shared/lib/chart-text";
import { cn } from "@/shared/lib/utils";
import {
  displayMoney,
  displayNumber,
  displayShortDate,
  displayShortMonthYear,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { RANKING_PRICE } from "../lib/fund-metrics";
import { FundSection } from "./fund-section";

// Teto e piso do preço de ranking em volta do patrimônio por cota
const RANKING_BAND = 0.3;

type Row = { time: number; day: string; price: number | null; nav: number };

function toRows(series: FundDetails["series"]): Row[] {
  return series.map((point) => ({
    time: parseLocalDate(point.day).getTime(),
    day: point.day,
    price: point.close === null ? null : Number(point.close),
    nav: Number(point.nav),
  }));
}

function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
      <span className={cn("size-2.5 rounded-full", color)} />
      {label}
    </span>
  );
}

/** O preço no mercado contra o patrimônio por cota, dia a dia, nos últimos 12 meses. */
function PriceChart({ fund }: { fund: FundDetails }) {
  const rows = toRows(fund.series);

  if (rows.length < 2) {
    return (
      <p className="py-10 text-center text-[13px] text-muted-foreground">
        O gráfico aparece depois dos primeiros pregões da gestora.
      </p>
    );
  }

  return (
    <div className="grid gap-2">
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={rows} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke="var(--border)" />
          <XAxis
            dataKey="time"
            type="number"
            scale="time"
            domain={["dataMin", "dataMax"]}
            tickFormatter={(time: number) => displayShortMonthYear(new Date(time))}
            tick={CHART_TICK}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={["auto", "auto"]}
            tickFormatter={(value: number) => displayNumber(value, 0)}
            tick={CHART_TICK}
            axisLine={false}
            tickLine={false}
            width={44}
          />
          <Tooltip
            cursor={{ stroke: "var(--foreground)", strokeOpacity: 0.4 }}
            content={({ active, payload }) => {
              const row = payload[0]?.payload as Row | undefined;
              if (!active || !row) return null;
              return (
                <div className="grid gap-0.5 rounded-lg border bg-popover px-2.5 py-1.5 text-xs shadow-md">
                  <span className="text-muted-foreground">{displayShortDate(row.day)}</span>
                  <span className="font-mono font-semibold">
                    Preço: {row.price === null ? "sem negócio" : displayMoney(row.price)}
                  </span>
                  <span className="font-mono text-muted-foreground">Patrimônio por cota: {displayMoney(row.nav)}</span>
                </div>
              );
            }}
          />
          <Line
            dataKey="nav"
            type="linear"
            stroke="var(--fund)"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
          <Line
            dataKey="price"
            type="linear"
            stroke="var(--chart-1)"
            strokeWidth={2}
            dot={false}
            connectNulls
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
      <div className="flex flex-wrap gap-4">
        <LegendDot color="bg-chart-1" label="Preço no mercado" />
        <LegendDot color="bg-fund" label="Patrimônio por cota" />
      </div>
    </div>
  );
}

/** O preço de ranking, que vale na carteira e no ranking, com o piso e o teto em volta do patrimônio por cota. */
function RankingPrice({ fund }: { fund: FundDetails }) {
  const nav = fund.nav === null ? null : Number(fund.nav);

  return (
    <FundSection title={<MetricLabel metric={RANKING_PRICE} />}>
      <div className="grid gap-3">
        <span className="font-mono text-[28px] leading-tight font-semibold tabular-nums">
          {fund.ranking_price === null ? "—" : displayMoney(fund.ranking_price)}
        </span>
        <p className="text-[13px] text-muted-foreground">{RANKING_PRICE.description}.</p>
        {nav !== null && (
          <div>
            <KeyValueRow label="Teto (patrimônio por cota + 30%)" value={displayMoney(nav * (1 + RANKING_BAND))} />
            <KeyValueRow label="Patrimônio por cota" value={displayMoney(nav)} />
            <KeyValueRow label="Piso (patrimônio por cota − 30%)" value={displayMoney(nav * (1 - RANKING_BAND))} />
          </div>
        )}
        <p className="text-xs text-muted-foreground">
          Média dos negócios dos últimos 20 pregões, pesada pelo tamanho de cada um.
        </p>
      </div>
    </FundSection>
  );
}

/** O gráfico preço x patrimônio por cota ao lado do preço de ranking. */
export function FundPriceChart({ fund }: { fund: FundDetails }) {
  return (
    <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_340px]">
      <FundSection title="Preço x patrimônio por cota · 12 meses">
        <PriceChart fund={fund} />
      </FundSection>
      <RankingPrice fund={fund} />
    </div>
  );
}
