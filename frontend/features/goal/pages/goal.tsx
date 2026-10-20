import { Navigate } from "react-router-dom";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { ErrorState } from "@/shared/components/error-state";
import { RaceStandings } from "@/shared/components/race-standings";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { useAuth } from "@/shared/hooks/useAuth";
import { useGoalProgress } from "@/shared/hooks/queries/useGoalProgress";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { GoalHero } from "../components/goal-hero";

export default function GoalPage() {
  usePageLabel("Meta");
  const { user } = useAuth();
  const { simulation } = useSimulation();
  const { data: progress, error, refetch } = useGoalProgress();
  const match = simulation?.simulation;

  // Sem meta não há corrida: a Clássica volta para a carteira
  if (!match || match.game_type === "CLASSIC") return <Navigate to="/portfolio" replace />;

  if (!progress) {
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

  return (
    <>
      <GoalHero progress={progress} grouping={match.player_grouping} teamNaming={match.team_naming} nickname={nickname} />

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
    </>
  );
}
