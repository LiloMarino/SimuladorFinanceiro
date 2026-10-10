import { useState } from "react";
import { Area, AreaChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { stringToColor } from "@/shared/lib/utils";
import { displayMoney, displayMoneyCompact, displayMonthYear, displayPercent, isLoss } from "@/shared/lib/utils/display";
import type { CompositionReport } from "@/types";
import { useStatisticsReport } from "../../hooks/queries/useStatisticsReport";
import { playerLabel } from "../../lib/player-label";
import { COMPOSITION, EFFECTIVE_SECTORS, SECTOR_EXPOSURE, SECTOR_PROFIT, displayMetric } from "../../lib/metrics";
import { MetricLabel } from "./metric-hint";
import { ChartCard, TabStatus, type ReportProps } from "./shared";

const UNCLASSIFIED = "Sem setor";

const LAYERS = [
  { key: "total_cash", label: "Caixa", color: "var(--color-chart-4)" },
  { key: "total_equity", label: "Renda variável", color: "var(--color-chart-1)" },
  { key: "total_fixed", label: "Renda fixa", color: "var(--color-chart-2)" },
] as const;

type PlayerComposition = CompositionReport["players"][number];

export function CompositionTab({ simulationIds, showSimulation, currentPlayerName }: ReportProps) {
  const { data, isLoading } = useStatisticsReport("composition", simulationIds);
  const [selected, setSelected] = useState<string | null>(null);
  if (!data) return <TabStatus loading={isLoading} />;

  const players = data.players.map((p) => ({ player: p, label: playerLabel(p, showSimulation) }));
  // Começa no jogador logado; sem ele na lista, no primeiro
  const current =
    players.find((p) => p.label === selected) ??
    players.find((p) => p.player.player_nickname === currentPlayerName) ??
    players[0];

  return (
    <div className="space-y-6">
      <ChartCard metric={COMPOSITION}>
        {players.length > 1 && (
          <div className="mb-4 flex flex-wrap gap-2">
            {players.map(({ label }) => (
              <button
                key={label}
                type="button"
                onClick={() => setSelected(label)}
                className={`flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium transition-all ${
                  label === current?.label ? "bg-primary/10 border-primary/20" : "opacity-60"
                }`}
              >
                <span className="size-3 rounded-full" style={{ backgroundColor: stringToColor(label) }} />
                {label}
              </button>
            ))}
          </div>
        )}
        {current ? <CompositionChart player={current.player} /> : null}
      </ChartCard>

      <ChartCard metric={SECTOR_EXPOSURE}>
        <div className="space-y-5">
          {players.map(({ player, label }) => (
            <SectorExposure key={label} player={player} label={label} />
          ))}
        </div>
      </ChartCard>

      <ChartCard metric={SECTOR_PROFIT}>
        <div className="space-y-6">
          {players.map(({ player, label }) => (
            <SectorProfit key={label} player={player} label={label} />
          ))}
        </div>
      </ChartCard>
    </div>
  );
}

function CompositionChart({ player }: { player: PlayerComposition }) {
  const data = player.history.map((h) => ({
    timestamp: new Date(`${h.snapshot_date}T00:00:00`).getTime(),
    total_cash: Number(h.total_cash),
    total_equity: Number(h.total_equity),
    total_fixed: Number(h.total_fixed),
  }));

  return (
    <div className="h-[380px]">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 12, right: 16, left: 24, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis
            dataKey="timestamp"
            type="number"
            scale="time"
            domain={["dataMin", "dataMax"]}
            tickFormatter={(v) => displayMonthYear(new Date(v))}
            minTickGap={40}
          />
          <YAxis tickFormatter={(v: number) => displayMoneyCompact(v)} width={96} />
          <Tooltip
            labelFormatter={(v: number) => displayMonthYear(new Date(v))}
            formatter={(value: number) => displayMoney(value)}
          />
          <Legend />
          {LAYERS.map((layer) => (
            <Area
              key={layer.key}
              type="monotone"
              dataKey={layer.key}
              name={layer.label}
              stackId="networth"
              stroke={layer.color}
              fill={layer.color}
              fillOpacity={0.35}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

function SectorExposure({ player, label }: { player: PlayerComposition; label: string }) {
  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
        <span className="font-medium">{label}</span>
        <span className="flex items-center gap-1 text-muted-foreground">
          <MetricLabel metric={EFFECTIVE_SECTORS} />: {displayMetric(EFFECTIVE_SECTORS, player.effective_sectors)}
        </span>
      </div>

      {player.sectors.length === 0 ? (
        <p className="text-sm text-muted-foreground">Nenhuma ação na carteira no último dia.</p>
      ) : (
        <>
          {/* Régua de 0 a 100% fatiada por setor */}
          <div className="flex h-4 w-full overflow-hidden rounded-full bg-muted">
            {player.sectors.map((s) => (
              <div
                key={s.sector ?? UNCLASSIFIED}
                title={`${s.sector ?? UNCLASSIFIED}: ${displayPercent(s.fraction)}`}
                style={{ width: `${Number(s.fraction) * 100}%`, backgroundColor: stringToColor(s.sector ?? UNCLASSIFIED) }}
              />
            ))}
          </div>
          <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
            {player.sectors.map((s) => (
              <span key={s.sector ?? UNCLASSIFIED} className="flex items-center gap-1">
                <span
                  className="size-2.5 rounded-full"
                  style={{ backgroundColor: stringToColor(s.sector ?? UNCLASSIFIED) }}
                />
                {s.sector ?? UNCLASSIFIED} {displayPercent(s.fraction)}
              </span>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function SectorProfit({ player, label }: { player: PlayerComposition; label: string }) {
  const largest = Math.max(...player.sector_profit.map((s) => Math.abs(Number(s.profit))), 0);

  return (
    <div className="space-y-2">
      <p className="text-sm font-medium">{label}</p>
      {player.sector_profit.length === 0 ? (
        <p className="text-sm text-muted-foreground">Nenhuma ação negociada.</p>
      ) : (
        player.sector_profit.map((s) => {
          const loss = isLoss(s.profit);
          const width = largest > 0 ? (Math.abs(Number(s.profit)) / largest) * 100 : 0;
          return (
            <div key={s.sector ?? UNCLASSIFIED} className="grid grid-cols-[minmax(0,12rem)_1fr_7rem] items-center gap-3">
              <span className="truncate text-xs text-muted-foreground">{s.sector ?? UNCLASSIFIED}</span>
              <div className="h-3 rounded-full bg-muted">
                <div
                  className={`h-3 rounded-full ${loss ? "bg-destructive" : "bg-success"}`}
                  style={{ width: `${width}%` }}
                />
              </div>
              <span className={`text-right text-xs font-medium ${loss ? "text-destructive" : "text-success"}`}>
                {displayMoney(s.profit)}
              </span>
            </div>
          );
        })
      )}
    </div>
  );
}
