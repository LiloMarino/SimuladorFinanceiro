import { Navigate } from "react-router-dom";
import { CardState } from "@/shared/components/card-state";
import { Skeleton } from "@/shared/components/ui/skeleton";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { hasProfessions } from "@/shared/lib/game-types";
import { IncomeSeriesSection } from "../components/income-series";
import { MechanicBlockSkeleton } from "../components/mechanic-block";
import { ProfessionHeader } from "../components/profession-header";
import { ProfessionHistory } from "../components/profession-history";
import { ProfessionMechanic } from "../components/profession-mechanic";
import { useProfessionPage } from "../hooks/queries/useProfessionPage";

export default function ProfessionPage() {
  usePageLabel("Profissão");
  const { simulation } = useSimulation();
  const match = simulation?.active ? simulation.simulation : null;
  const { data: page, error, refetch } = useProfessionPage();

  // A página existe só na partida com profissões
  if (!match || !hasProfessions(match)) return <Navigate to="/portfolio" replace />;

  if (!page) {
    return (
      <CardState
        bare
        label="Carregando a profissão"
        error={error}
        onRetry={() => void refetch()}
        errorTitle="Não deu para carregar sua profissão"
      >
        <Skeleton className="h-52" />
        <MechanicBlockSkeleton />
        <Skeleton className="h-64" />
      </CardState>
    );
  }

  return (
    <div className="grid gap-5">
      <ProfessionHeader page={page} match={match} />
      <ProfessionMechanic mechanic={page.mechanic} />
      <IncomeSeriesSection series={page.series} />
      <ProfessionHistory />
    </div>
  );
}
