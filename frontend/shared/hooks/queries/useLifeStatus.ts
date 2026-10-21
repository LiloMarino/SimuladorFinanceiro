import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useSimulation } from "@/shared/hooks/useSimulation";
import type { LifeStatus } from "@/types";

/**
 * A vida financeira de quem vê a tela no viver de renda. Só o viver de renda tem vida
 * financeira: nos outros tipos a busca nem sai. O dado muda quando o caixa muda; quem renova
 * é o LifeNotifications, nos eventos cash_update e life_event.
 */
export function useLifeStatus() {
  const { simulation } = useSimulation();
  const current = simulation?.active ? simulation.simulation : null;

  return useQuery({
    queryKey: queryKeys.lifeStatus(current?.id ?? 0),
    queryFn: ({ signal }) => apiFetch<LifeStatus>("/api/simulation/life", { signal }),
    enabled: current?.game_type === "FINANCIAL_INDEPENDENCE",
  });
}
