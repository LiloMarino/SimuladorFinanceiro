import { useState } from "react";
import { Spinner } from "@/shared/components/ui/spinner";
import { useAuth } from "@/shared/hooks/useAuth";
import { PerformanceChart } from "../components/performance-chart";
import { PlayersRankingTable } from "../components/players-ranking-table";
import { SimulationPicker } from "../components/simulation-picker";
import { useSimulationComparison } from "../hooks/queries/useSimulationComparison";

export default function CompareSimulationsPage() {
  const [selected, setSelected] = useState<number[]>([]);
  const { data: comparison, isLoading: loading, error } = useSimulationComparison(selected);
  const { user: currentUser } = useAuth();

  const toggle = (id: number) =>
    setSelected((prev) => (prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id].sort((a, b) => a - b)));

  const renderContent = () => {
    if (selected.length === 0) {
      return <EmptyState message="Selecione simulações na lista para comparar." />;
    }

    if (loading) {
      return (
        <div className="flex h-72 items-center justify-center">
          <Spinner className="size-6" />
        </div>
      );
    }

    if (error || !comparison) {
      return <EmptyState message="Erro ao carregar a comparação." />;
    }

    return (
      <>
        <PerformanceChart players={comparison.players} showSimulation />
        <PlayersRankingTable
          players={comparison.players}
          currentPlayerName={currentUser?.nickname ?? ""}
          showSimulation
        />
      </>
    );
  };

  return (
    <div className="flex h-full flex-col md:flex-row">
      <SimulationPicker selected={selected} onToggle={toggle} />

      <section className="min-w-0 flex-1 space-y-6 p-4">{renderContent()}</section>
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex h-72 items-center justify-center rounded-md border border-dashed text-sm text-muted-foreground">
      {message}
    </div>
  );
}
