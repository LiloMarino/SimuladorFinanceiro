import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { eventAccountKey } from "@/shared/lib/active-account";
import { queryKeys } from "@/shared/lib/queryKeys";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { TreasuryPosition } from "@/types";

/** Os títulos do jogador na conta ativa; o preço de mercado muda todo dia, e o servidor entrega a lista de cada conta por `treasury_positions_update`. */
export function useTreasuryPositions() {
  const queryClient = useQueryClient();
  const { accountKey } = useActiveAccount();

  useRealtime("treasury_positions_update", ({ positions, account }) => {
    if (eventAccountKey(account) !== accountKey) return;
    void applyRealtime<TreasuryPosition[]>(queryClient, queryKeys.treasuryPositions(), positions);
  });

  return useQuery({
    queryKey: queryKeys.treasuryPositions(),
    queryFn: ({ signal }) => apiFetch<TreasuryPosition[]>("/api/treasury/positions", { signal, activeAccount: true }),
    staleTime: 0,
  });
}
