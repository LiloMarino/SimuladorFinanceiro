import { Skeleton } from "@/shared/components/ui/skeleton";
import { ErrorState } from "@/shared/components/error-state";
import { useStatisticsReport } from "@/shared/hooks/queries/useStatisticsReport";
import { teamColor, teamName } from "@/shared/lib/teams";
import { displayNumber } from "@/shared/lib/utils/display";
import { SCORE_HISTORY } from "../../lib/metrics";
import { labelColors, playerLabel, youLabel } from "../../lib/player-label";
import { PlayerLineChart, type LineSeries } from "./player-line-chart";
import { ChartCard, type ReportProps } from "./shared";

/** A nota total mês a mês: uma linha por jogador, ou por equipe na partida em equipes. */
export function ScoreHistoryCard({ simulationIds, currentPlayerName = "", onlyPlayer }: ReportProps) {
  const { data, isLoading, error, refetch } = useStatisticsReport("score-history", simulationIds, onlyPlayer);

  if (!data) {
    return (
      <ChartCard metric={SCORE_HISTORY}>
        {isLoading ? (
          <Skeleton className="h-85" />
        ) : (
          <ErrorState
            title="Não deu pra carregar a nota ao longo da partida"
            description="O resto do Geral continua funcionando."
            error={error}
            onRetry={() => void refetch()}
          />
        )}
      </ChartCard>
    );
  }

  const colorOf = labelColors(data.players, simulationIds, currentPlayerName);
  const yourTeam = data.players.find((p) => p.player_nickname === currentPlayerName)?.team;
  const series: LineSeries[] =
    data.player_grouping === "TEAMS"
      ? data.teams.map((t) => ({
          key: `team-${t.team}`,
          label: teamName(t.team, data.team_naming),
          color: teamColor(t.team),
          points: t.points,
          emphasis: t.team === yourTeam,
        }))
      : data.players.map((p) => {
          const label = playerLabel(p, simulationIds, currentPlayerName);
          const isYou = p.player_nickname === currentPlayerName;
          return { key: label, label: youLabel(label, isYou), color: colorOf(label), points: p.points, emphasis: isYou };
        });

  return (
    <ChartCard metric={SCORE_HISTORY}>
      <PlayerLineChart
        key={series.map((s) => s.key).join("|")}
        series={series}
        format={(v) => displayNumber(v, 0)}
        axisFormat={(v) => displayNumber(v, 0)}
        emptyMessage="A nota aparece a partir de 63 pregões; o gráfico começa no primeiro mês com nota."
      />
    </ChartCard>
  );
}
