import { useCallback, useEffect, type PropsWithChildren } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { AuthContext } from "./AuthContext";
import type { Session } from "@/types";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { queryKeys } from "@/shared/lib/queryKeys";

export function AuthProvider({ children }: PropsWithChildren) {
  const queryClient = useQueryClient();

  // Mutation: Inicializa uma nova sessão
  const { mutateAsync: initSession, isPending: initLoading } = useApiMutation({
    mutationFn: () => apiFetch<Session>("/api/session/init", { method: "POST", body: {} }),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.authSession(), data);
    },
  });

  // Query: Sessão atual
  const { data: session, isLoading: sessionLoading } = useApiQuery({
    queryKey: queryKeys.authSession(),
    queryFn: ({ signal }) => apiFetch<Session>("/api/session/me", { signal }),
  });

  // Mutation: Logout
  const { mutateAsync: logoutApi, isPending: logoutLoading } = useApiMutation({
    mutationFn: () => apiFetch<void>("/api/session/logout", { method: "POST", body: {} }),
    onSuccess: async () => {
      queryClient.setQueryData(queryKeys.authSession(), null);
    },
  });

  // Mutation: Delete account
  const { mutateAsync: deleteAccountApi, isPending: deleteLoading } = useApiMutation({
    mutationFn: () => apiFetch<void>("/api/user", { method: "DELETE" }),
    onSuccess: async () => {
      queryClient.setQueryData(queryKeys.authSession(), null);
    },
  });

  // Inicializa sessão apenas uma vez na montagem
  useEffect(() => {
    const init = async () => {
      await initSession();
    };
    init();
  }, [initSession]);

  const logout = useCallback(async () => {
    await logoutApi();

    // Garante novo client_id após logout
    await initSession();
  }, [initSession, logoutApi]);

  const deleteAccount = useCallback(async () => {
    await deleteAccountApi();

    // Garante novo client_id após exclusão
    await initSession();
  }, [initSession, deleteAccountApi]);

  return (
    <AuthContext.Provider
      value={{
        session: session ?? null,
        user: session?.user ?? null,
        logout,
        deleteAccount,
        loading: sessionLoading || initLoading || logoutLoading || deleteLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
