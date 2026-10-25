import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";

/** O dia da partida agora: as contagens regressivas seguem o relógio, não a data em que o painel foi montado. */
export function useToday(panel: { today: string }) {
  const { data } = useSimulationState();
  return data?.current_date ?? panel.today;
}
