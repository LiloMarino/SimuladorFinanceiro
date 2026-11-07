import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { cn } from "@/shared/lib/utils";
import { PlayerName } from "./player-name";
import { displayNumber, displaySignedPercent } from "@/shared/lib/utils/display";
import type { ReturnsPlayer } from "@/types";
import {
  PLAYER_GROUPS,
  playerPoints,
  segmentLayout,
  type PlayerGroupKey,
  type PlayerSourcePoint,
} from "../../lib/return-sources";

interface Row {
  player: ReturnsPlayer;
  label: string;
  isYou: boolean;
  points: PlayerSourcePoint[];
  total: number;
}

const GROUP_LABELS: Record<PlayerGroupKey, string> = {
  appreciation: "Valorização",
  dividends: "Proventos",
  fixed_income_interest: "Juro da renda fixa",
  costs: "IR e juro de dívida",
};

/** Cada jogador numa barra que sai do zero: ganhos para a direita, custos para a esquerda, em pontos do retorno. */
export function ReturnSourcesByPlayerCard({
  players,
}: {
  players: { player: ReturnsPlayer; label: string; isYou: boolean }[];
}) {
  const rows: Row[] = players.flatMap(({ player, label, isYou }) => {
    const points = playerPoints(player.return_sources, Number(player.capital_provided));
    return points ? [{ player, label, isYou, points, total: points.reduce((sum, p) => sum + p.points, 0) }] : [];
  });
  if (rows.length === 0) return null;

  // O custo ganha o nome da campanha quando algum jogador gastou nela
  const hasCampaign = rows.some(({ player }) => Number(player.return_sources.campaign) !== 0);
  const labels = { ...GROUP_LABELS, costs: hasCampaign ? "IR, dívida e campanha" : GROUP_LABELS.costs };

  const reach = (side: 1 | -1) =>
    Math.max(
      0,
      ...rows.map(({ points }) => points.reduce((sum, p) => (p.points * side > 0 ? sum + Math.abs(p.points) : sum), 0)),
    );
  const right = reach(1);
  const left = reach(-1);
  const span = right + left || 1;
  const zero = (left / span) * 100;

  const example = rows.find((row) => row.total > 0 && (row.points.find((p) => p.key === "dividends")?.points ?? 0) > 0);
  const exampleDividends = example?.points.find((p) => p.key === "dividends")?.points ?? 0;

  return (
    <Card>
      <CardHeader className="grid-cols-[1fr_auto]">
        <div className="grid gap-1">
          <CardTitle>Origem do retorno por jogador</CardTitle>
          <CardDescription>
            Em pontos do retorno
            {example &&
              `: na barra de ${example.label}, ${displayNumber(exampleDividends * 100, 1)} dos ${displayNumber(example.total * 100, 1)}% vieram de proventos`}
            .
          </CardDescription>
        </div>
        <ul className="flex flex-wrap gap-3.5 text-xs text-muted-foreground">
          {PLAYER_GROUPS.map(({ key, bar }) => (
            <li key={key} className="flex items-center gap-1.5">
              <span className={cn("size-2.5 rounded-[3px]", bar)} aria-hidden="true" />
              {labels[key]}
            </li>
          ))}
        </ul>
      </CardHeader>
      <CardContent>
        <div className="grid gap-1">
          {rows.map((row) => (
            <div
              key={`${row.player.simulation_id}|${row.player.player_nickname}`}
              className={cn(
                "grid grid-cols-[minmax(0,140px)_minmax(0,1fr)_72px] items-center gap-4 rounded-lg px-3 py-2",
                row.isYou && "bg-muted/50",
              )}
            >
              <span className="truncate text-[13px] font-medium">
                <PlayerName label={row.label} isYou={row.isYou} />
              </span>
              <div className="relative h-[26px]">
                <i className="absolute inset-y-0 w-px bg-input" style={{ left: `${zero}%` }} />
                <SegmentBars points={row.points} span={span} zero={zero} labels={labels} />
              </div>
              <b
                className={cn("text-right font-mono text-[13px]", row.total >= 0 ? "text-success" : "text-destructive")}
              >
                {displaySignedPercent(row.total, 1)}
              </b>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function SegmentBars({
  points,
  span,
  zero,
  labels,
}: {
  points: PlayerSourcePoint[];
  span: number;
  zero: number;
  labels: Record<PlayerGroupKey, string>;
}) {
  return (
    <>
      {segmentLayout(points, span, zero).map(({ point, start, width }) => (
        <Tooltip key={point.key}>
          <TooltipTrigger
            render={<span className="absolute inset-y-0" style={{ left: `${start}%`, width: `${width}%` }} />}
          >
            <i className={cn("block h-full rounded-[3px] border-x border-card", point.bar)} />
          </TooltipTrigger>
          <TooltipContent>
            {labels[point.key]}: {displaySignedPercent(point.points, 1)} do aporte
          </TooltipContent>
        </Tooltip>
      ))}
    </>
  );
}
