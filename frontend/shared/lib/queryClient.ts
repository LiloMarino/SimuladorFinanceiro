import { QueryClient } from "@tanstack/react-query";
import ApiError from "@/shared/lib/models/ApiError";

export const queryClient = new QueryClient({
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
