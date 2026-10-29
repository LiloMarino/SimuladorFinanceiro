import { useSimulation } from "@/shared/hooks/useSimulation";
import { JournalPaper } from "../components/journal-paper";

export default function JournalPage() {
  const { simulation } = useSimulation();
  const simulationId = simulation?.simulation?.id;
  if (simulationId === undefined) return null;

  return <JournalPaper simulationId={simulationId} />;
}
