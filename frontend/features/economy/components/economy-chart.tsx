import { useState } from "react";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceDot,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { InfoHint } from "@/shared/components/info-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { displayDate, displayPercent, displayShortMonthYear } from "@/shared/lib/utils/display";
import { signedIpca } from "@/shared/lib/effects";
import type { EconomyPanel } from "@/types";
import { copomLabel, economyRows, effectShares, type EconomyRange, type EconomyRow } from "../lib/economy";
import { IPCA, REAL_RATE, SELIC } from "../lib/economy-metrics";

const TICK = { fontSize: 10.5, fill: "var(--faint-foreground)" };
const SELIC_COLOR = "var(--chart-1)";
const IPCA_COLOR = "var(--chart-2)";
const TARGET_COLOR = "var(--muted-foreground)";

type EconomyChartProps = { panel: EconomyPanel };

/** `measured`: a partida tem a expansão Governo, e a linha tracejada mostra a história sem as medidas. */
function Legend({ measured }: { measured: boolean }) {
  return (
    <ul className="flex flex-wrap items-center gap-x-5 gap-y-1.5 text-xs text-muted-foreground">
      <li className="flex items-center gap-1.5">
        <span className="h-0.5 w-5 rounded-full" style={{ background: SELIC_COLOR }} />
        SELIC (juro básico)
      </li>
      <li className="flex items-center gap-1.5">
        <span className="h-0.5 w-5 rounded-full" style={{ background: IPCA_COLOR }} />
        IPCA em 12 meses (inflação)
      </li>
      <li className="flex items-center gap-1.5">
        <span
          className="h-2.5 w-5 border-y-2 border-dashed"
          style={{
            borderColor: TARGET_COLOR,
            background: "color-mix(in srgb, var(--muted-foreground) 14%, transparent)",
          }}
        />
        Meta e tolerância
      </li>
      <li className="flex items-center gap-1.5">
        <span className="size-2 rounded-full ring-2 ring-card" style={{ background: SELIC_COLOR }} />
        Mudança da SELIC pelo Copom
      </li>
      {measured && (
        <li className="flex items-center gap-1.5">
          <span className="h-0 w-5 border-t-2 border-dashed" style={{ borderColor: IPCA_COLOR }} />
          <span className="h-0 w-5 border-t-2 border-dashed" style={{ borderColor: SELIC_COLOR }} />
          na história, sem as medidas
        </li>
      )}
    </ul>
  );
}

function EconomyTooltip({
  active,
  payload,
  effects,
}: {
  active?: boolean;
  payload?: { payload: EconomyRow }[];
  effects: EconomyPanel["effects"];
}) {
  const row = payload?.[0]?.payload;
  if (!active || !row) return null;
  const shares = effects ? effectShares(effects, row.time) : [];
  return (
    <div className="grid gap-1 rounded-lg border bg-popover px-2.5 py-2 text-xs shadow-md">
      <span className="text-muted-foreground">{displayDate(new Date(row.time))}</span>
      <span className="flex items-center justify-between gap-6">
        <span>SELIC</span>
        <span className="font-mono font-semibold">{displayPercent(row.selic, 2)}</span>
      </span>
      {row.storedSelic !== null && (
        <span className="flex items-center justify-between gap-6 text-muted-foreground">
          <span>SELIC na história</span>
          <span className="font-mono">{displayPercent(row.storedSelic, 2)}</span>
        </span>
      )}
      <span className="flex items-center justify-between gap-6">
        <span>IPCA em 12 meses</span>
        <span className="font-mono font-semibold">{displayPercent(row.ipca, 2)}</span>
      </span>
      {row.storedIpca !== null && (
        <span className="flex items-center justify-between gap-6 text-muted-foreground">
          <span>IPCA na história</span>
          <span className="font-mono">{displayPercent(row.storedIpca, 2)}</span>
        </span>
      )}
      {shares.map((share) => (
        <span key={share.label} className="flex items-center justify-between gap-6 pl-2 text-muted-foreground">
          <span>{share.label}</span>
          <span className="font-mono">{signedIpca(share.points)}</span>
        </span>
      ))}
      <span className="flex items-center justify-between gap-6">
        <span>Juro real</span>
        <span className="font-mono font-semibold">{displayPercent(row.realRate, 2)}</span>
      </span>
      <span className="flex items-center justify-between gap-6">
        <span>Meta do ano</span>
        <span className="font-mono font-semibold">{displayPercent(row.target, 2)}</span>
      </span>
      <span className="flex items-center justify-between gap-6">
        <span>Faixa da meta</span>
        <span className="font-mono font-semibold">
          {displayPercent(row.band[0], 2)} a {displayPercent(row.band[1], 2)}
        </span>
      </span>
      {row.copom && <span className="border-t pt-1 font-medium">{copomLabel(row.copom)}</span>}
    </div>
  );
}

/** A SELIC e o IPCA desde o primeiro dia, com a meta de inflação do ano e os dias em que o Copom mexeu na SELIC. */
export function EconomyChart({ panel }: EconomyChartProps) {
  const [range, setRange] = useState<EconomyRange>("all");
  const rows = economyRows(panel, range);
  const today = panel.points.at(-1);
  const changes = rows.filter((row) => row.copom !== undefined);
  const measured = panel.effects !== null;

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-3.5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-1.5">
              <h2 className="text-[15px] font-semibold">Juros e inflação</h2>
              <InfoHint label="Como ler o gráfico">
                <div className="space-y-1 text-left">
                  <p>
                    {SELIC.description}: a linha azul. {IPCA.description}: a linha verde.
                  </p>
                  <p>
                    A distância entre as duas é o {REAL_RATE.label.toLowerCase()}: SELIC de 10% com IPCA de 4% deixa 6%
                    de rendimento de verdade.
                  </p>
                  <p>
                    Com a SELIC bem acima da inflação, o dinheiro parado rende de verdade; com a inflação acima dela,
                    perde. A linha tracejada é a meta de inflação do ano, e a faixa em volta dela é a tolerância.
                  </p>
                </div>
              </InfoHint>
            </div>
            <ToggleGroup
              variant="segmented"
              aria-label="Período do gráfico"
              value={[range]}
              onValueChange={(values) => values[0] && setRange(values[0] as EconomyRange)}
            >
              <ToggleGroupItem value="all">Desde o início</ToggleGroupItem>
              <ToggleGroupItem value="year">12 meses</ToggleGroupItem>
            </ToggleGroup>
          </div>

          <Legend measured={measured} />

          {rows.length < 2 ? (
            <div className="flex h-72 items-center justify-center rounded-[10px] border border-dashed border-input text-sm text-muted-foreground">
              O gráfico aparece quando a partida andar um pouco.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <ComposedChart data={rows} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
                <CartesianGrid vertical={false} stroke="var(--border)" />
                <XAxis
                  dataKey="time"
                  type="number"
                  scale="time"
                  domain={["dataMin", "dataMax"]}
                  tickFormatter={(time: number) => displayShortMonthYear(new Date(time))}
                  tick={TICK}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  domain={[(min: number) => Math.min(0, min), "auto"]}
                  tickFormatter={(value: number) => displayPercent(value, 0)}
                  tick={TICK}
                  axisLine={false}
                  tickLine={false}
                  width={40}
                />
                <Tooltip
                  cursor={{ stroke: "var(--foreground)", strokeOpacity: 0.4 }}
                  content={<EconomyTooltip effects={panel.effects} />}
                />
                <Area
                  dataKey="band"
                  type="stepAfter"
                  stroke="none"
                  fill={TARGET_COLOR}
                  fillOpacity={0.14}
                  activeDot={false}
                  isAnimationActive={false}
                />
                <Line
                  dataKey="target"
                  type="stepAfter"
                  stroke={TARGET_COLOR}
                  strokeWidth={1.5}
                  strokeDasharray="5 4"
                  dot={false}
                  activeDot={false}
                  isAnimationActive={false}
                />
                {measured && (
                  <Line
                    dataKey="storedIpca"
                    type="linear"
                    stroke={IPCA_COLOR}
                    strokeWidth={1.5}
                    strokeDasharray="6 3"
                    dot={false}
                    activeDot={false}
                    isAnimationActive={false}
                  />
                )}
                {measured && (
                  <Line
                    dataKey="storedSelic"
                    type="linear"
                    stroke={SELIC_COLOR}
                    strokeWidth={1.5}
                    strokeDasharray="6 3"
                    dot={false}
                    activeDot={false}
                    isAnimationActive={false}
                  />
                )}
                <Line
                  dataKey="ipca"
                  type="linear"
                  stroke={IPCA_COLOR}
                  strokeWidth={2}
                  dot={false}
                  isAnimationActive={false}
                />
                <Line
                  dataKey="selic"
                  type="linear"
                  stroke={SELIC_COLOR}
                  strokeWidth={2}
                  dot={false}
                  isAnimationActive={false}
                />
                {changes.map((row) => (
                  <ReferenceDot
                    key={row.time}
                    x={row.time}
                    y={row.selic}
                    r={3.5}
                    fill={SELIC_COLOR}
                    stroke="var(--card)"
                    strokeWidth={2}
                    ifOverflow="visible"
                  />
                ))}
              </ComposedChart>
            </ResponsiveContainer>
          )}

          {measured && (
            <p className="text-[12.5px] text-muted-foreground">
              Linha cheia: a partida. Tracejada: o que aconteceu de verdade (ou o futuro gerado, depois do último dado
              real), sem as medidas de gasto do governo. A distância entre as duas é o efeito das medidas.
            </p>
          )}

          {today && (
            <p className="text-[12.5px] text-muted-foreground">
              O Banco Central sobe a SELIC quando o IPCA passa da meta e corta quando fica abaixo. Juro real de hoje:{" "}
              {displayPercent(today.selic, 2)} − {displayPercent(today.ipca, 2)} = {displayPercent(today.real_rate, 2)}.
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
