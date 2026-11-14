import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { FundAccount } from "@/types";

// O caixa de uma gestora não chega por tempo real ao jogador: a lista se renova sozinha
const REFRESH_MS = 10_000;

/** As contas com que o jogador opera: a pessoal primeiro e depois cada gestora que ele gere. Só existe com a expansão Gestoras ligada. */
export function useFundAccounts({ enabled = true }: { enabled?: boolean } = {}) {
  return useQuery({
    queryKey: queryKeys.fundAccounts(),
    queryFn: ({ signal }) => apiFetch<FundAccount[]>("/api/funds/accounts", { signal }),
    enabled,
    refetchInterval: REFRESH_MS,
  });
}
