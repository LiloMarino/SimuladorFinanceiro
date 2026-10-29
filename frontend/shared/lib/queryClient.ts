import { MutationCache, QueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/shared/lib/queryKeys";
import ApiError from "@/shared/lib/models/ApiError";

// `apiFetch` sempre rejeita com ApiError: toda query e mutation herda esse tipo de erro
declare module "@tanstack/react-query" {
  interface Register {
    defaultError: ApiError;
  }
}

export const queryClient = new QueryClient({
  // Toda ação do jogador pode resolver ou criar uma pendência: a lista confere depois de cada uma
  mutationCache: new MutationCache({
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: queryKeys.pending() }),
  }),
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5min
      gcTime: 10 * 60 * 1000, // 10min
      // Erros 4xx (404, 400, etc.) são definitivos — tentar de novo só atrasa
      // o estado de erro. Erros de rede/5xx continuam com até 2 retentativas.
      retry: (failureCount, error) => {
        if (error instanceof ApiError && error.status >= 400 && error.status < 500) return false;
        return failureCount < 2;
      },
      refetchOnWindowFocus: true, // Refetch ao voltar na aba
      refetchOnReconnect: true, // Refetch ao reconectar internet
    },
  },
});
