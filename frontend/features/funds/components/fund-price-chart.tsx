import { useState } from "react";
import { Area, CartesianGrid, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Kpi } from "@/shared/components/kpi";
import { MetricLabel } from "@/shared/components/metric-hint";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { FundSection } from "@/shared/components/fund-section";
import { CHART_TICK } from "@/shared/lib/chart-text";
import { RANKING_BAND, RANKING_PRICE } from "@/shared/lib/fund-metrics";
import { cn } from "@/shared/lib/utils";
import {
  displayMoney,
  displayNumber,
  displayShortDate,
  displayShortMonthYear,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { RANKING_BAND_FRACTION, rangeCutoff, RANGES, type PriceRange } from "../lib/fund-price-range";

type Row = {
  time: number;
  day: string;
  price: number | null;
  nav: number;
  ranking: number | null;
  band: [number, number];
};

function toRows(series: FundDetails["series"]): Row[] {
  return series.map((point) => {
    const nav = Number(point.nav);
    return {
      time: parseLocalDate(point.day).getTime(),
      day: point.day,
      price: point.close === null ? null : Number(point.close),
      nav,
      ranking: point.ranking_price === null ? null : Number(point.ranking_price),
      band: [nav * (1 - RANKING_BAND_FRACTION), nav * (1 + RANKING_BAND_FRACTION)],
    };
  });
}

function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
      <span className={cn("size-2.5 rounded-full", color)} />
      {label}
    </span>
  );
}

/** O preço no mercado, o patrimônio por cota e o preço de ranking dentro da faixa de ±30%, dia a dia. */
function PriceChart({ rows }: { rows: Row[] }) {
  if (rows.length < 2) {
    return (
      <p className="py-10 text-center text-[13px] text-muted-foreground">
        O gráfico aparece depois dos primeiros pregões da gestora.
      </p>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <ComposedChart data={rows} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
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
                <span className="font-mono text-muted-foreground">
                  Preço de ranking: {row.ranking === null ? "—" : displayMoney(row.ranking)}
                </span>
              </div>
            );
          }}
        />
        <Area
          dataKey="band"
          type="linear"
          stroke="none"
          fill="var(--fund)"
          fillOpacity={0.08}
          isAnimationActive={false}
        />
        <Line dataKey="nav" type="linear" stroke="var(--fund)" strokeWidth={2} dot={false} isAnimationActive={false} />
        <Line
          dataKey="ranking"
          type="linear"
          stroke="var(--fund)"
          strokeWidth={1.5}
          strokeDasharray="4 3"
          dot={false}
          connectNulls
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
      </ComposedChart>
    </ResponsiveContainer>
  );
}

/** O card "Preço da cota": janela do gráfico, o preço de ranking, a faixa de hoje e as linhas. */
export function FundPriceChart({ fund }: { fund: FundDetails }) {
  const [range, setRange] = useState<PriceRange>("6m");
  const all = toRows(fund.series);
  const last = all.at(-1);
  const cutoff = last ? rangeCutoff(range, last.day) : 0;
  const rows = all.filter((row) => row.time >= cutoff);
  const nav = fund.nav === null ? null : Number(fund.nav);

  return (
    <FundSection
      title="Preço da cota"
      action={
        <ToggleGroup
          variant="segmented"
          aria-label="Janela do gráfico"
          value={[range]}
          onValueChange={(values) => {
            const next = RANGES.find((item) => item.value === values[0]);
            if (next) setRange(next.value);
          }}
        >
          {RANGES.map((item) => (
            <ToggleGroupItem key={item.value} value={item.value}>
              {item.label}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
      }
    >
      <div className="grid gap-4">
        {/* Preço de ranking e faixa de hoje */}
        <div className="grid grid-cols-2 gap-x-6 gap-y-3">
          <Kpi
            label={<MetricLabel metric={RANKING_PRICE} />}
            value={fund.ranking_price === null ? "—" : displayMoney(fund.ranking_price)}
            note={RANKING_PRICE.description}
          />
          <Kpi
            label={<MetricLabel metric={RANKING_BAND} />}
            value={
              nav === null
                ? "—"
                : `${displayMoney(nav * (1 - RANKING_BAND_FRACTION))} a ${displayMoney(nav * (1 + RANKING_BAND_FRACTION))}`
            }
            note="30% abaixo e acima do patrimônio por cota"
          />
        </div>

        {/* Gráfico */}
        <PriceChart rows={rows} />

        {/* Legenda */}
        <div className="flex flex-wrap gap-4">
          <LegendDot color="bg-chart-1" label="Preço no mercado" />
          <LegendDot color="bg-fund" label="Patrimônio por cota" />
          <LegendDot color="bg-fund/60" label="Preço de ranking" />
          <LegendDot color="bg-fund/10" label="Faixa de ±30%" />
        </div>
      </div>
    </FundSection>
  );
}
