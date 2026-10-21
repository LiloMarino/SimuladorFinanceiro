import { useCallback } from "react";
import { toast } from "sonner";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { TunnelStatus } from "@/types";

export function useTunnel() {
    const queryClient = useQueryClient();

    // Query para obter status inicial
    const { data: status, refetch: refetchStatus } = useQuery({
        queryKey: queryKeys.tunnelStatus(),
        queryFn: ({ signal }) => apiFetch<TunnelStatus>("/api/tunnel/status", { signal }),
    });

    // Mutation para iniciar túnel
    const { mutate: startTunnelMutate, isPending: startingTunnel } = useMutation({
        mutationFn: () => apiFetch<TunnelStatus>("/api/tunnel/start", { method: "POST" }),
        onSuccess: (data) => {
            toast.success(`Túnel iniciado com sucesso!`);
            queryClient.setQueryData(queryKeys.tunnelStatus(), data);
        },
        onError: (err) => {
            toast.error(`Erro ao iniciar túnel: ${err.message}`);
        },
    });

    // Mutation para parar túnel
    const { mutate: stopTunnelMutate, isPending: stoppingTunnel } = useMutation({
        mutationFn: () => apiFetch<void>("/api/tunnel/stop", { method: "POST" }),
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
