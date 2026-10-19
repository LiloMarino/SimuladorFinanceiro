import type { ReactNode } from "react";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { TeamBadge } from "@/shared/components/team-badge";
import { Card } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { MetricHint } from "@/shared/components/metric-hint";
import type { MetricInfo } from "@/shared/lib/metric-info";
import { cn } from "@/shared/lib/utils";
import {
  displayMoney,
  displayMonthSlashYear,
  displayNumber,
  displayPercent,
  displaySignedPercent,
} from "@/shared/lib/utils/display";
import type { Highlights, TeamNaming } from "@/types";
import { useStatisticsReport } from "../../hooks/queries/useStatisticsReport";
import { CUMULATIVE_RETURN, INCOME_TAX_PAID, MAX_DRAWDOWN } from "../../lib/metrics";

interface HighlightProps {
  label: string;
  metric?: MetricInfo;
  value: ReactNode;
  tone?: "positive" | "negative";
  player: string | undefined;
  color: string | undefined;
  /** Equipe de quem lidera, quando a partida é em equipes: o escudo vai ao lado do nome */
  team?: { index: number | null | undefined; naming: TeamNaming };
}

function Highlight({ label, metric, value, tone, player, color, team }: HighlightProps) {
  return (
    <Card size="sm">
      <div className="grid gap-1.5 px-4">
        <span className="flex items-center gap-1 text-xs font-medium text-muted-foreground">
          {label}
          {metric && <MetricHint metric={metric} />}
        </span>
        <span
          className={cn(
            "font-mono text-lg font-semibold",
            tone === "positive" && "text-success",
            tone === "negative" && "text-destructive",
          )}
        >
          {player ? value : "—"}
        </span>
        <span className="flex items-center gap-1.5 text-xs">
          {player ? (
            <>
              <PlayerAvatar nickname={player} color={color} size="sm" />
              {player}
              {team?.index ? <TeamBadge team={team.index} naming={team.naming} form="icon" size="sm" /> : null}
            </>
          ) : (
            <span className="text-muted-foreground">Ninguém nesta partida</span>
          )}
        </span>
      </div>
    </Card>
  );
}

// Zero fica neutro: nem ganhou nem perdeu
function toneOf(value: string | undefined) {
  if (value === undefined || Number(value) === 0) return undefined;
  return Number(value) > 0 ? "positive" : "negative";
}

interface HighlightsRowProps {
  simulationId: number;
  currentPlayerName?: string;
  /** Cor de quem está vendo, para o "seu melhor mês" */
  currentPlayerColor?: string;
  /** Equipe de cada jogador (por apelido) e como as equipes se chamam; vazio fora do modo em equipes */
  teamOf?: (nickname: string | undefined) => number | null | undefined;
  teamNaming?: TeamNaming;
}

/** Quem foi melhor em quê na partida, e o seu melhor mês. */
export function HighlightsRow({
  simulationId,
  currentPlayerName,
  currentPlayerColor,
  teamOf,
  teamNaming = "COLOR",
}: HighlightsRowProps) {
  const { data } = useStatisticsReport("highlights", [simulationId]);
  if (!data) return <HighlightsSkeleton />;

  const item = (h: Highlights["biggest_return"]) => ({
    player: h?.player_nickname,
    color: h?.color,
    team: teamOf ? { index: teamOf(h?.player_nickname), naming: teamNaming } : undefined,
  });
  const best = data.your_best_month;

  return (
    <div className="grid gap-3.5 sm:grid-cols-2 lg:grid-cols-5">
      <Highlight
        label="Maior retorno"
        metric={CUMULATIVE_RETURN}
        value={data.biggest_return && displaySignedPercent(data.biggest_return.value)}
        tone={toneOf(data.biggest_return?.value)}
        {...item(data.biggest_return)}
      />
      <Highlight
        label="Menor queda"
        metric={MAX_DRAWDOWN}
        value={data.smallest_drawdown && displayPercent(data.smallest_drawdown.value)}
        {...item(data.smallest_drawdown)}
      />
      <Highlight
        label="Mais negócios"
        value={data.most_trades && displayNumber(data.most_trades.value, 0)}
        {...item(data.most_trades)}
      />
      <Highlight
        label="Mais IR pago"
        metric={INCOME_TAX_PAID}
        value={data.most_tax && displayMoney(data.most_tax.value)}
        {...item(data.most_tax)}
      />
      <Highlight
        label="Seu melhor mês"
        value={best && `${displaySignedPercent(best.value)} · ${displayMonthSlashYear(best.month)}`}
        tone={toneOf(best?.value)}
        player={best ? currentPlayerName : undefined}
        color={currentPlayerColor}
        team={teamOf ? { index: teamOf(currentPlayerName), naming: teamNaming } : undefined}
      />
    </div>
  );
}

export function HighlightsSkeleton() {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
      {Array.from({ length: 5 }, (_, i) => (
        <Skeleton key={i} className="h-[76px]" />
      ))}
    </div>
  );
}
