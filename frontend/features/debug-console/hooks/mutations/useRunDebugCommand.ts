import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { DebugCommandResult } from "@/types";

export function useRunDebugCommand() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (line: string) =>
      apiFetch<DebugCommandResult>("/api/debug/command", { method: "POST", body: { line } }),
    // O comando muda a partida: as escolhas do catálogo (títulos, partidos, jogadores) voltam a ser lidas
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.debugCommands() }),
  });
}
