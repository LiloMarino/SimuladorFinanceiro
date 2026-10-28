import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { PromisesPanel } from "@/types";

/** As promessas da chapa de quem fundou o partido: a lista anunciada, as medidas que se prometem e o prazo. */
export function usePromises(enabled: boolean) {
  return useQuery({
    queryKey: queryKeys.promises(),
    queryFn: ({ signal }) => apiFetch<PromisesPanel>("/api/government/promises", { signal }),
    enabled,
  });
}
