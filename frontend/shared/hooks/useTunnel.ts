import { useCallback } from "react";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { queryKeys } from "@/shared/lib/queryKeys";

export type TunnelStatus = {
    active: boolean;
    url: string | null;
    provider: string | null;
};

export function useTunnel() {
    const queryClient = useQueryClient();

    // Query para obter status inicial
    const { data: status, refetch: refetchStatus } = useApiQuery({
        queryKey: queryKeys.tunnelStatus(),
        queryFn: ({ signal }) => apiFetch<TunnelStatus>("/api/tunnel/status", { signal }),
    });

    // Mutation para iniciar túnel
    const { mutate: startTunnelMutate, isPending: startingTunnel } = useApiMutation({
        mutationFn: () => apiFetch<{ url: string; provider: string }>("/api/tunnel/start", { method: "POST" }),
        onSuccess: (data) => {
            toast.success(`Túnel iniciado com sucesso!`);
            queryClient.setQueryData(queryKeys.tunnelStatus(), {
                active: true,
                url: data.url,
                provider: data.provider,
            });
        },
        onError: (err) => {
            toast.error(`Erro ao iniciar túnel: ${err.message}`);
        },
    });

    // Mutation para parar túnel
    const { mutate: stopTunnelMutate, isPending: stoppingTunnel } = useApiMutation({
        mutationFn: () => apiFetch<{ message: string }>("/api/tunnel/stop", { method: "POST" }),
        onSuccess: () => {
            toast.success("Túnel parado com sucesso!");
            queryClient.setQueryData(queryKeys.tunnelStatus(), {
                active: false,
                url: null,
                provider: null,
            });
        },
        onError: (err) => {
            toast.error(`Erro ao parar túnel: ${err.message}`);
        },
    });

    return {
        status,
        startTunnel: useCallback(() => startTunnelMutate(), [startTunnelMutate]),
        stopTunnel: useCallback(() => stopTunnelMutate(), [stopTunnelMutate]),
        refetchStatus,
        loading: startingTunnel || stoppingTunnel,
    };
}
