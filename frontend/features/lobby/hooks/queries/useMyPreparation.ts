import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { MyPreparation } from "@/types";

/** O que da preparação só o jogador vê: convite recebido, convite enviado e o partido que saiu da sala. */
export function useMyPreparation() {
  const queryClient = useQueryClient();
  const key = queryKeys.myPreparation();

  const query = useQuery({
    queryKey: key,
    queryFn: ({ signal }) => apiFetch<MyPreparation>("/api/simulation/players/me/preparation", { signal }),
  });

  // A chave mora sob a de preparations: as invalidações dela já chegam aqui
  useRealtime("preparations_update", () => void queryClient.invalidateQueries({ queryKey: key }));

  return query;
}
