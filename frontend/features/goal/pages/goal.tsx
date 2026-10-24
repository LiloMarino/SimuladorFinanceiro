import { Navigate } from "react-router-dom";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { ErrorState } from "@/shared/components/error-state";
import { RaceStandings } from "@/shared/components/race-standings";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { useAuth } from "@/shared/hooks/useAuth";
import { useGoalProgress } from "@/shared/hooks/queries/useGoalProgress";
import { useLifeStatus } from "@/shared/hooks/queries/useLifeStatus";
import { usePatrimonialHistory } from "@/shared/hooks/queries/usePatrimonialHistory";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { projectGoalDate } from "@/shared/lib/goal";
import { GoalHero } from "../components/goal-hero";
import { LifeCard } from "../components/life-card";
import { LifeHistory } from "../components/life-history";
import { hasGoal } from "@/shared/lib/game-types";

export default function GoalPage() {
  usePageLabel("Meta");
  const { user } = useAuth();
  const { simulation } = useSimulation();
  const { data: progress, error, refetch } = useGoalProgress();
  const { data: life } = useLifeStatus();
  const { data: state } = useSimulationState();
  const { data: history } = usePatrimonialHistory();
  const match = simulation?.simulation;
  const independence = match?.game_type === "FINANCIAL_INDEPENDENCE";

  // Sem meta não há corrida: a Clássica volta para a carteira
  if (!match || !hasGoal(match.game_type)) return <Navigate to="/portfolio" replace />;

  // O viver de renda só abre com a vida financeira e o caixa na mão
  if (!progress || (independence && (!life || state?.cash === undefined))) {
    return error ? (
      <Card>
        <CardContent>
          <ErrorState
            title="Não deu pra carregar a corrida"
            description="A partida continua rodando. Tente de novo; se persistir, o servidor do host pode ter caído."
            error={error}
            onRetry={() => void refetch()}
          />
        </CardContent>
      </Card>
    ) : (
      <div className="grid gap-5">
        <Skeleton className="h-52" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  const nickname = user?.nickname ?? "";
  const projection = projectGoalDate(history ?? [], progress.goal);

  return (
    <>
      <GoalHero
        gameType={match.game_type}
        progress={progress}
        life={life}
        projection={projection}
        grouping={match.player_grouping}
        teamNaming={match.team_naming}
        nickname={nickname}
      />

      <div className={independence ? "grid items-start gap-5 lg:grid-cols-[1fr_1.1fr]" : undefined}>
        {/* Corrida de todos */}
        <Card>
          <CardHeader>
            <CardTitle>Corrida</CardTitle>
            <CardDescription>
              {match.player_grouping === "TEAMS"
                ? "Cada equipe vale a média do patrimônio dos membros. A partida termina no dia em que alguma chegar."
                : "A partida termina no dia em que alguém chegar."}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <RaceStandings
              progress={progress}
              grouping={match.player_grouping}
              teamNaming={match.team_naming}
              currentNickname={nickname}
            />
          </CardContent>
        </Card>

        {/* Vida financeira */}
        {life && state?.cash !== undefined && (
          <LifeCard life={life} match={match} cash={state.cash} projection={projection} />
        )}
      </div>

      {/* Histórico */}
      {life && <LifeHistory life={life} />}
    </>
  );
}
