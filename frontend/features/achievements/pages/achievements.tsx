import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useAchievements } from "@/shared/hooks/queries/useAchievements";
import { useSimulationSettings } from "@/shared/hooks/queries/useSimulationSettings";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { Achievement } from "@/types";
import { AchievementsList } from "../components/achievements-list";
import { AchievementsPanelSkeleton } from "../components/achievements-skeleton";
import { AchievementsSidePanel } from "../components/achievements-side-panel";
import { useMarkAchievementsSeen } from "../hooks/mutations/useMarkAchievementsSeen";

export default function AchievementsPage() {
  const { data: achievements, error, refetch } = useAchievements();
  const { data: settings } = useSimulationSettings();
  const { simulation, simulationActive } = useSimulation();

  // Convidado lê as conquistas guardadas no computador do host
  const guestOf = settings && !settings.is_host ? settings.host_nickname : undefined;

  return (
    <section className="grid gap-5">
      {/* Título: dentro da partida quem o mostra é a barra do topo */}
      {!simulationActive && (
        <h1 className="text-lg font-semibold">Conquistas</h1>
      )}

      <span className="max-w-190 text-muted-foreground">
        Objetivos para buscar além de vencer a partida. Cada uma sai uma vez só, na partida em que você chegou lá.
      </span>

      <div className="grid items-start gap-5 lg:grid-cols-[minmax(0,1fr)_320px]">
        <AchievementsList
          achievements={achievements}
          error={error}
          onRetry={() => void refetch()}
          guestOf={guestOf}
          canPlay={simulationActive}
        />
        {/* O painel acompanha a lista: sem lista, sem contadores */}
        {achievements ? (
          <LoadedPanel
            achievements={achievements}
            currentSimulationId={simulationActive ? simulation?.simulation?.id : undefined}
          />
        ) : (
          !error && <AchievementsPanelSkeleton />
        )}
      </div>
    </section>
  );
}

type LoadedPanelProps = {
  achievements: Achievement[];
  currentSimulationId?: number;
};

/** Painel com a lista já resolvida; abrir a tela é o que marca as conquistas como vistas. */
function LoadedPanel({ achievements, currentSimulationId }: LoadedPanelProps) {
  const queryClient = useQueryClient();
  const { mutateAsync: markSeen } = useMarkAchievementsSeen();

  // O selo "Nova" fica à mostra enquanto a tela está aberta; ao sair, a lista renova sem ele e o ponto do menu apaga
  useEffect(() => {
    const done = markSeen().catch(() => undefined);
    return () => {
      void done.then(() => queryClient.invalidateQueries({ queryKey: queryKeys.achievements() }));
    };
  }, [markSeen, queryClient]);

  return <AchievementsSidePanel achievements={achievements} currentSimulationId={currentSimulationId} />;
}
