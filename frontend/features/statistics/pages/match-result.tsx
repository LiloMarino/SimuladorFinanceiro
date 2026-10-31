import { Flag } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/shared/components/ui/empty";
import { ErrorState } from "@/shared/components/error-state";
import { useAuth } from "@/shared/hooks/useAuth";
import type ApiError from "@/shared/lib/models/ApiError";
import { useSimulationList } from "@/shared/hooks/queries/useSimulationList";
import { BacktestResultView } from "../components/backtest-result/backtest-result-view";
import { HighlightsRow, HighlightsSkeleton } from "../components/match-result/highlights-row";
import { MatchAchievements } from "../components/match-result/match-achievements";
import { MatchHero, MatchHeroSkeleton } from "../components/match-result/match-hero";
import { TeamPullers } from "../components/match-result/team-pullers";
import { StatisticsReport } from "../components/statistics-report";
import { useStatisticsReport } from "@/shared/hooks/queries/useStatisticsReport";

export default function MatchResultPage() {
  const { simulationId } = useParams();
  const id = Number(simulationId);
  if (!Number.isInteger(id)) return null;

  return <ResultKind simulationId={id} />;
}

/** Backtest e partida fecham de jeitos diferentes: o tipo vem da lista de salvas. */
function ResultKind({ simulationId }: { simulationId: number }) {
  const { data: simulations, isPending, isFetching, error, refetch } = useSimulationList({ refetchOnMount: "always" });
  const simulation = simulations?.find((s) => s.id === simulationId);

  // O erro vem antes do esqueleto: sem a lista não há como saber o tipo da partida
  if (error && !simulations) {
    return (
      <ResultErrorCard
        title="Não conseguimos abrir a partida"
        description="A lista de partidas salvas não respondeu. Tente de novo ou volte ao lobby."
        error={error}
        onRetry={() => void refetch()}
      />
    );
  }

  // Uma simulação recém-salva ainda não está na lista em cache: espera a busca trazê-la
  if (isPending || (!simulation && isFetching)) {
    return (
      <div className="grid gap-5">
        <MatchHeroSkeleton />
        <HighlightsSkeleton />
      </div>
    );
  }
  if (simulation?.is_backtest) {
    return <BacktestResultView simulationId={simulationId} />;
  }
  return <MatchResult simulationId={simulationId} />;
}

const backToLobby = (
  <Button variant="outline" nativeButton={false} render={<Link to="/lobby" />}>
    Voltar ao lobby
  </Button>
);

function ResultErrorCard({
  title,
  description,
  error,
  onRetry,
}: {
  title: string;
  description: string;
  error: ApiError;
  onRetry: () => void;
}) {
  return (
    <Card>
      <CardContent>
        <ErrorState title={title} description={description} error={error} onRetry={onRetry}>
          {backToLobby}
        </ErrorState>
      </CardContent>
    </Card>
  );
}

/** Fechamento da partida: o vencedor e o pódio, os destaques e o relatório da partida inteira. */
function MatchResult({ simulationId }: { simulationId: number }) {
  const { user } = useAuth();
  const { data: overview, error, refetch } = useStatisticsReport("overview", [simulationId]);
  const { data: simulations } = useSimulationList();

  if (error && !overview) {
    return (
      <ResultErrorCard
        title="Não conseguimos carregar o resultado"
        description="A partida terminou e está salva. Tente de novo ou volte ao lobby: o resultado fica em “Simulações salvas”."
        error={error}
        onRetry={() => void refetch()}
      />
    );
  }

  if (overview && overview.players.length === 0) {
    return (
      <Card>
        <CardContent>
          <Empty>
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <Flag />
              </EmptyMedia>
              <EmptyTitle>Essa partida terminou sem resultado</EmptyTitle>
              <EmptyDescription>
                Ninguém chegou a ter patrimônio registrado: ela foi encerrada antes do primeiro pregão.
              </EmptyDescription>
            </EmptyHeader>
            <EmptyContent>
              <Button nativeButton={false} render={<Link to="/lobby" />}>
                Voltar ao lobby
              </Button>
            </EmptyContent>
          </Empty>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-5">
      {overview ? (
        <>
          <MatchHero
            report={overview}
            simulation={simulations?.find((s) => s.id === simulationId)}
            currentPlayerName={user?.nickname}
          />
          {overview.teams.length > 0 && <TeamPullers report={overview} currentPlayerName={user?.nickname} />}
          <HighlightsRow
            simulationId={simulationId}
            currentPlayerName={user?.nickname}
            currentPlayerColor={overview.players.find((p) => p.player_nickname === user?.nickname)?.color}
            teamOf={
              overview.teams.length > 0
                ? (nickname) => overview.players.find((p) => p.player_nickname === nickname)?.team
                : undefined
            }
            teamNaming={overview.team_naming}
          />
          <MatchAchievements simulationId={simulationId} />
        </>
      ) : (
        <>
          <MatchHeroSkeleton />
          <HighlightsSkeleton />
        </>
      )}

      {/* Relatório da partida: as mesmas abas das Estatísticas, congeladas no último dia */}
      <StatisticsReport
        title="Relatório da partida"
        simulationIds={[simulationId]}
        currentPlayerName={user?.nickname}
      />
    </div>
  );
}
