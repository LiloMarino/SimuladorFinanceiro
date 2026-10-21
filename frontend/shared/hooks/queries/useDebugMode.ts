import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/shared/hooks/useAuth";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { DebugMode } from "@/types";

/**
 * Se o servidor subiu em modo debug (`--debug` ou `[debug] enabled` no config.toml).
 * O valor é do boot do servidor e não muda com o app aberto, então é lido uma vez.
 * Query própria: o cache das notificações recebe o valor otimista sem esse campo.
 * `isPending` separa "ainda não sei" de "desligado", e `error` de "o servidor não respondeu",
 * para a tela não decidir cedo demais nem tratar falha como modo desligado.
 */
export function useDebugStatus() {
  // O endpoint é por usuário: só responde depois do login (então as ferramentas não
  // aparecem na tela de login). Ao entrar, a sessão muda e a query dispara sozinha.
  const { session } = useAuth();

  const { data, isPending, error, refetch } = useQuery({
    queryKey: queryKeys.debugMode(),
    queryFn: ({ signal }) => apiFetch<{ debug: DebugMode }>("/api/settings", { signal }),
    select: (settings) => settings.debug,
    staleTime: Infinity,
    enabled: !!session?.authenticated,
  });

  return { debug: data ?? false, isPending, error, refetch };
}

export function useDebugMode(): DebugMode {
  return useDebugStatus().debug;
}
