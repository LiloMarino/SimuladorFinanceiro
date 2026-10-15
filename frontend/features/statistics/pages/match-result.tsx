import { Flag } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
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
import { simulationListOptions } from "@/shared/lib/queries/simulationListOptions";
import { HighlightsRow, HighlightsSkeleton } from "../components/match-result/highlights-row";
import { MatchHero, MatchHeroSkeleton } from "../components/match-result/match-hero";
import { StatisticsReport } from "../components/statistics-report";
import { useStatisticsReport } from "../hooks/queries/useStatisticsReport";
import { playerColors } from "../lib/player-colors";

export default function MatchResultPage() {
  const { simulationId } = useParams();
  const id = Number(simulationId);
  if (!Number.isInteger(id)) return null;

  return <MatchResult simulationId={id} />;
}

const backToLobby = (
  <Button variant="outline" nativeButton={false} render={<Link to="/lobby" />}>
    Voltar ao lobby
  </Button>
);

/** Fechamento da partida: o vencedor e o pódio, os destaques e o relatório da partida inteira. */
function MatchResult({ simulationId }: { simulationId: number }) {
  const { user } = useAuth();
  const { data: overview, error, refetch } = useStatisticsReport("overview", [simulationId]);
  const { data: simulations } = useQuery(simulationListOptions());

  if (error && !overview) {
    return (
      <Card>
        <CardContent>
          <ErrorState
            title="Não conseguimos carregar o resultado"
            description="A partida terminou e está salva. Tente de novo ou volte ao lobby: o resultado fica em “Simulações salvas”."
            error={error}
            onRetry={() => void refetch()}
          >
            {backToLobby}
          </ErrorState>
        </CardContent>
      </Card>
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

  const colorOf = playerColors(overview?.players.map((p) => p.player_nickname) ?? []);

  return (
    <div className="grid gap-5">
      {overview ? (
        <>
          <MatchHero
            report={overview}
            simulation={simulations?.find((s) => s.id === simulationId)}
            currentPlayerName={user?.nickname}
            colorOf={colorOf}
          />
          <HighlightsRow simulationId={simulationId} currentPlayerName={user?.nickname} colorOf={colorOf} />
        </>
      ) : (
        <>
          <MatchHeroSkeleton />
          <HighlightsSkeleton />
        </>
      )}

      {/* Relatório da partida */}
      <section className="grid gap-3">
        <div>
          <h2 className="text-[15px] font-semibold">Relatório da partida</h2>
          <p className="text-[13px] text-muted-foreground">
            As mesmas abas das Estatísticas, congeladas no último dia da partida.
          </p>
        </div>
        <StatisticsReport simulationIds={[simulationId]} currentPlayerName={user?.nickname} />
      </section>
    </div>
  );
}
