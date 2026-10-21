import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { TunnelStatus } from "@/types";

export function useStartTunnel() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => apiFetch<TunnelStatus>("/api/tunnel/start", { method: "POST" }),
    onSuccess: (data) => {
      toast.success("Túnel iniciado com sucesso!");
      queryClient.setQueryData(queryKeys.tunnelStatus(), data);
    },
    onError: (err) => toast.error(`Erro ao iniciar túnel: ${err.message}`),
  });
}
