import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5min
      gcTime: 10 * 60 * 1000, // 10min
      retry: 2,
      refetchOnWindowFocus: true, // Refetch ao voltar na aba
      refetchOnReconnect: true, // Refetch ao reconectar internet
    },
  },
});
