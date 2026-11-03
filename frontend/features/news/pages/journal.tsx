import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { JournalPaper } from "../components/journal-paper";

export default function JournalPage() {
  const { simulation } = useSimulation();
  const { data: state } = useSimulationState();
  const settings = simulation?.simulation;
  if (!settings || !state?.current_date) return null;

  return <JournalPaper simulationId={settings.id} startDate={settings.start_date} currentDate={state.current_date} />;
}
