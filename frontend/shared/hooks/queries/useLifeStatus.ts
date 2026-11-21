import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useSimulation } from "@/shared/hooks/useSimulation";
import type { LifeStatus } from "@/types";

/**
 * A vida financeira de quem vê a tela no viver de renda. Só o viver de renda tem vida
 * financeira: nos outros tipos a busca nem sai. O dado muda quando o caixa muda e a cada
 * dia: o servidor entrega a vida financeira nova por `life_status_update`.
 */
export function useLifeStatus() {
  const queryClient = useQueryClient();
  const { simulation } = useSimulation();
  const current = simulation?.active ? simulation.simulation : null;
  const independence = current?.game_type === "FINANCIAL_INDEPENDENCE";
  const queryKey = queryKeys.lifeStatus(current?.id ?? 0);

  useRealtime(
    "life_status_update",
    ({ status }) => {
      void applyRealtime<LifeStatus>(queryClient, queryKey, status);
    },
    independence,
  );

  return useQuery({
    queryKey,
    queryFn: ({ signal }) => apiFetch<LifeStatus>("/api/simulation/life", { signal }),
    enabled: independence,
    staleTime: 0,
  });
}
