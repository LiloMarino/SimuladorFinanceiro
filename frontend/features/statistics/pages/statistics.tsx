import { useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/shared/hooks/useAuth";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { queryKeys } from "@/shared/lib/queryKeys";
import { StatisticsReport } from "../components/statistics-report";
import { UpdateNotice } from "../components/update-notice";

export default function StatisticsPage() {
  const queryClient = useQueryClient();
  const { simulation } = useSimulation();
  const { user } = useAuth();

  // O snapshot que as abas leem fecha o mês: todas as abas abertas refazem a busca
  useRealtime("statistics_snapshot_update", () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.statistics() });
  });

  const simulationId = simulation?.simulation?.id;
  if (simulationId === undefined) return null;

  return (
    <section className="space-y-3">
      <UpdateNotice />
      <StatisticsReport simulationIds={[simulationId]} currentPlayerName={user?.nickname} />
    </section>
  );
}
