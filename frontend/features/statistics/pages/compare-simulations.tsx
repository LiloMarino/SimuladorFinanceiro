import { useState } from "react";
import { useAuth } from "@/shared/hooks/useAuth";
import { SimulationPicker } from "../components/simulation-picker";
import { StatisticsReport } from "../components/statistics-report";

export default function CompareSimulationsPage() {
  const [selected, setSelected] = useState<number[]>([]);
  const { user: currentUser } = useAuth();

  const toggle = (id: number) =>
    setSelected((prev) => (prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id].sort((a, b) => a - b)));

  return (
    <div className="flex h-full flex-col md:flex-row">
      <SimulationPicker selected={selected} onToggle={toggle} />

      <section className="min-w-0 flex-1 p-4">
        {selected.length === 0 ? (
          <EmptyState message="Selecione simulações na lista para comparar." />
        ) : (
          <StatisticsReport simulationIds={selected} showSimulation currentPlayerName={currentUser?.nickname} />
        )}
      </section>
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
