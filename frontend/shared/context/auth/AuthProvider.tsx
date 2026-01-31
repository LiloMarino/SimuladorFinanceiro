import { useCallback, useEffect, type PropsWithChildren } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AuthContext } from "./AuthContext";
import type { Session } from "@/types/user";
import { handleApiResponse } from "@/shared/lib/utils/api";

export function AuthProvider({ children }: PropsWithChildren) {
  const queryClient = useQueryClient();

  // Mutation: Inicializa uma nova sessão
  const { mutateAsync: initSession, isPending: initLoading } = useMutation({
    mutationFn: async () => {
      const res = await fetch("/api/session/init", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({}),
      });
      return handleApiResponse<Session>(res);
    },
    onSuccess: (data) => {
      queryClient.setQueryData(["auth", "session"], data);
    },
  });

  // Query: Sessão atual
  const { data: session, isLoading: sessionLoading } = useQuery({
    queryKey: ["auth", "session"],
    queryFn: async () => {
      const res = await fetch("/api/session/me", { credentials: "include" });
      return handleApiResponse<Session>(res);
    },
  });

  // Mutation: Logout
  const { mutateAsync: logoutApi, isPending: logoutLoading } = useMutation({
    mutationFn: async () => {
      const res = await fetch("/api/session/logout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({}),
      });
      return handleApiResponse<void>(res);
    },
    onSuccess: async () => {
      queryClient.setQueryData(["auth", "session"], null);
    },
  });

  // Mutation: Delete account
  const { mutateAsync: deleteAccountApi, isPending: deleteLoading } = useMutation({
    mutationFn: async () => {
      const res = await fetch("/api/user", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
      });
      return handleApiResponse<void>(res);
    },
    onSuccess: async () => {
      queryClient.setQueryData(["auth", "session"], null);
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
