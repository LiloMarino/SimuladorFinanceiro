import { useCallback } from "react";
import { toast } from "sonner";
import { useMutationApi } from "./useMutationApi";
import { useQueryApi } from "./useQueryApi";

export type TunnelStatus = {
    active: boolean;
    url: string | null;
    provider: string | null;
};

export function useTunnel() {
    // Query para obter status inicial
    const { data: status, setData: setStatus, query: refetchStatus } = useQueryApi<TunnelStatus>("/api/tunnel/status", {
        initialFetch: true,
    });

    // Mutation para iniciar túnel
    const { mutate: startTunnel, loading: startingTunnel } = useMutationApi<
        { url: string; provider: string }
    >("/api/tunnel/start", {
        method: "POST",
        onSuccess: (data) => {
            toast.success(`Túnel iniciado com sucesso!`);
            setStatus({
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
    const { mutate: stopTunnel, loading: stoppingTunnel } = useMutationApi<
        { message: string }
    >("/api/tunnel/stop", {
        method: "POST",
        onSuccess: () => {
            toast.success("Túnel parado com sucesso!");
            setStatus({
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
        startTunnel: useCallback(() => startTunnel({}), [startTunnel]),
        stopTunnel: useCallback(() => stopTunnel({}), [stopTunnel]),
        refetchStatus,
        loading: startingTunnel || stoppingTunnel,
    };
}
