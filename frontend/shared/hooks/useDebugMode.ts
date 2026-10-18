import { useAuth } from "@/shared/hooks/useAuth";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { DebugMode } from "@/types";

/**
 * Se o servidor subiu em modo debug (`--debug` ou `[debug] enabled` no config.toml).
 * O valor é do boot do servidor e não muda com o app aberto, então é lido uma vez.
 * Query própria: o cache das notificações recebe o valor otimista sem esse campo.
 */
export function useDebugMode(): DebugMode {
  // O endpoint é por usuário: só responde depois do login (então as ferramentas não
  // aparecem na tela de login). Ao entrar, a sessão muda e a query dispara sozinha.
  const { session } = useAuth();

  const { data } = useApiQuery({
    queryKey: queryKeys.debugMode(),
    queryFn: ({ signal }) => apiFetch<{ debug: DebugMode }>("/api/settings", { signal }),
    select: (settings) => settings.debug,
    staleTime: Infinity,
    enabled: !!session?.authenticated,
  });

  return data ?? false;
}
