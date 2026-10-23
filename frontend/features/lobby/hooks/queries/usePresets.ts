import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { Preset } from "@/types";

/** Os presets de partida: os prontos do app e os que o host salvou. Só o host lê. */
export function usePresets({ enabled = true }: { enabled?: boolean } = {}) {
  return useQuery({
    queryKey: queryKeys.presets(),
    queryFn: ({ signal }) => apiFetch<Preset[]>("/api/presets", { signal }),
    enabled,
  });
}
