import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { useMutationApi } from "./useMutationApi";
import { useQueryApi } from "./useQueryApi";
import { useRealtime } from "./useRealtime";

/**
 * Status do túnel retornado pelo backend
 */
export type TunnelStatus = {
    active: boolean;
    url: string | null;
    provider: string | null;
    enabled: boolean;
};

/**
 * Hook para gerenciar túnel de rede.
 * 
 * Funcionalidades:
 * - Consulta status do túnel
 * - Inicia/para túnel (apenas host)
 * - Escuta eventos realtime (tunnel_started, tunnel_stopped, tunnel_error)
 * - Exibe toasts automáticos em caso de erro
 * 
 * @example
 * ```tsx
 * const { status, startTunnel, stopTunnel, loading } = useTunnel();
 * 
 * if (status?.active) {
 *   console.log("Túnel ativo:", status.url);
 * }
 * 
 * // Iniciar túnel
 * await startTunnel();
 * ```
 */
export function useTunnel() {
    const [status, setStatus] = useState<TunnelStatus | null>(null);

    // Query para obter status inicial
    const { data: initialStatus, query: refetchStatus } = useQueryApi<TunnelStatus>("/api/tunnel/status", {
        initialFetch: true,
    });

    // Mutation para iniciar túnel
    const { mutate: startTunnel, loading: startingTunnel } = useMutationApi<
        { url: string; provider: string }
    >("/api/tunnel/start", {
        method: "POST",
        onSuccess: (data) => {
            toast.success(`Túnel iniciado com sucesso!`);
            setStatus((prev) => ({
                ...prev,
                active: true,
                url: data.url,
                provider: data.provider,
                enabled: prev?.enabled ?? false,
            }));
        },
        onError: (err) => {
            toast.error(`Erro ao iniciar túnel: ${err.message}`);
        },
    });

    // Mutation para parar túnel
    const { mutate: stopTunnel, loading: stoppingTunnel } = useMutationApi<
        { message: string }>("/api/tunnel/stop", {
            method: "POST",
            onSuccess: () => {
                toast.success("Túnel parado com sucesso!");
                setStatus((prev) => ({
                    ...prev,
                    active: false,
                    url: null,
                    provider: null,
                    enabled: prev?.enabled ?? false,
                }));
            },
            onError: (err) => {
                toast.error(`Erro ao parar túnel: ${err.message}`);
            },
        });

    // Atualiza status local quando query retorna
    useEffect(() => {
        if (initialStatus) {
            setStatus(initialStatus);
        }
    }, [initialStatus]);

    // Escuta evento tunnel_started via realtime
    useRealtime("tunnel_started", (event) => {
        setStatus((prev) => ({
            ...prev,
            active: true,
            url: event.url,
            provider: event.provider,
            enabled: prev?.enabled ?? false,
        }));
    });

    // Escuta evento tunnel_stopped via realtime
    useRealtime("tunnel_stopped", () => {
        setStatus((prev) => ({
            ...prev,
            active: false,
            url: null,
            provider: null,
            enabled: prev?.enabled ?? false,
        }));
    });

    // Escuta evento tunnel_error via realtime e exibe toast
    useRealtime("tunnel_error", (event) => {
        toast.error(`Erro no túnel: ${event.message}`);
    });

    const loading = startingTunnel || stoppingTunnel;

    return {
        status,
        startTunnel: useCallback(() => startTunnel({}), [startTunnel]),
        stopTunnel: useCallback(() => stopTunnel({}), [stopTunnel]),
        refetchStatus,
        loading,
    };
}
