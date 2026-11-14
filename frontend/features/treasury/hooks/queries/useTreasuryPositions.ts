import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { TreasuryPosition } from "@/types";

/** Os títulos do jogador; o preço de mercado muda todo dia, então a lista renova a cada dia da partida. */
export function useTreasuryPositions() {
  const queryClient = useQueryClient();

  useRealtime("simulation_update", () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.treasuryPositions() });
  });

  return useQuery({
    queryKey: queryKeys.treasuryPositions(),
    queryFn: ({ signal }) => apiFetch<TreasuryPosition[]>("/api/treasury/positions", { signal, activeAccount: true }),
  });
}
