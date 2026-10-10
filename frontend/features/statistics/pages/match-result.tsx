import { useNavigate, useParams } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";
import { useAuth } from "@/shared/hooks/useAuth";
import { Podium } from "../components/podium";
import { StatisticsReport } from "../components/statistics-report";
import { useStatisticsReport } from "../hooks/queries/useStatisticsReport";

export default function MatchResultPage() {
  const { simulationId } = useParams();
  const id = Number(simulationId);
  if (!Number.isInteger(id)) return null;

  return <MatchResult simulationId={id} />;
}

/** Fechamento da partida: o pódio pelo critério de vitória e o relatório da partida inteira. */
function MatchResult({ simulationId }: { simulationId: number }) {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { data: overview, isLoading } = useStatisticsReport("overview", [simulationId]);

  return (
    <section className="mx-auto max-w-6xl space-y-6 p-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Fim de partida</h1>
          {overview?.players[0] && <p className="text-muted-foreground">{overview.players[0].simulation_name}</p>}
        </div>
        <Button onClick={() => navigate("/lobby")}>Voltar ao lobby</Button>
      </div>

      {overview ? (
        overview.players.length > 0 ? (
          <Podium report={overview} />
        ) : (
          <p className="text-muted-foreground">Nenhum jogador chegou a ter patrimônio registrado nesta partida.</p>
        )
      ) : (
        <div className="flex h-40 items-center justify-center">
          {isLoading ? <Spinner className="size-6" /> : "Erro ao carregar o resultado."}
        </div>
      )}

      <StatisticsReport simulationIds={[simulationId]} showSimulation={false} currentPlayerName={user?.nickname} />
    </section>
  );
}
